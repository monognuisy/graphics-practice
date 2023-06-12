# Cow Rollercoaster

## Modified
Only modified `SimpleScene.py`. 

### Global variables

- `C_MAX`
  - number of cows. 6
- `LOOP_NUM`
  - number of loops. 3
- `cows`
    ```python
    cows=[None for i in range(C_MAX)]
    ```
- `cowCount`
  - to indicate number of cows(stamped) 
- `clickPos`
  - screen position when mouse clicked
- `isStart`
  - is the start of loop?
- `startTime`
  - start time of the loop
- `resCow`
  - result cow of the loop
- `bspline`
  - matrix for b-spline


### `display` function

In the stamping scenario (where `cowCount` is less or equal then `C_MAX`), we expect to see current holding cow and stamped cows.


To make the stamped cow visible, need to `drawCow` not only current cow (holding `cow2wld`), but also `cows` which indicates stamped cows. Only cow in `cows` not `None` are shown.

```python
if cowCount <= C_MAX:
    drawCow(cow2wld, cursorOnCowBoundingBox);														# Draw cow.

    for i in range(C_MAX):
        if (cows[i] is None):
            continue
        drawCow(cows[i], False);
```

In loop(cycle) scenario, we expect to see the cow follows the trajectory made by calculating B-spline curve with stamped cows. 
For this, the calculation of matrix of B-spline curve and direction of cow's head is necessary.
Following code shows the steps for these.

```python
# start roller-coaster
elif cowCount > C_MAX:
    if not isStart:
        resCow = cows[0].copy();
        isStart = True;
        startTime = glfw.get_time();
    t = glfw.get_time() - startTime;

    if t < LOOP_NUM*C_MAX :
        for i in range(C_MAX):
            if i < t % C_MAX and t % C_MAX < i + 1:
                t = t % 1
                P0 = cows[(i-1)%C_MAX] 
                P1 = cows[i%C_MAX]
                P2 = cows[(i+1)%C_MAX]
                P3 = cows[(i+2)%C_MAX]
                bspline = BSpline(P0, P1, P2, P3, t);
                resCow[:3, :3] = getHeadTransform(P0, P1, P2, P3, t);
                break;
    else:   
        # after rollercoaster
        isStart = 0
        cowCount = 0
        cow2wld = cows[0].copy() # reset cow position
        isDrag = 0 # drag initialize

        cows = [None for i in range(C_MAX)];
        glFlush()
        return 
    
    setTranslation(resCow, getTranslation(bspline));
    drawCow(resCow, False);
```

### `BSpline` function

This function calculates B-spline curve. The equation for this curve is as follows:
$$
{\bf p}(t) = {\bf b}(t) ^\top {\bf P}
$$

where $\bf P$ is vector with given 4-points and ${\bf b}(t)$ is 
$$
{\bf b}(t) = \frac{1}{6}\begin{bmatrix}
(1-t)^3 \\
3t^3 - 6t^2 + 4 \\
-3t^3 + 3t^2 + 3t + 1 \\
t^3
\end{bmatrix}
$$

### `getHeadTransform` function

This function returns a matrix indicating the head direction and rotation of cow.

First calculate derivative of B-spline curve and pick only translation part and normalize it. Then calculate pitch and yaw for expressing rotation of the cow.

With given(calculated) directional vector ${\rm d} = (d_x, d_y, d_z)^\top$ , the pitch and yaw are 
$$
\begin{align*}
{\rm pitch} &= \arctan\left(\dfrac{d_x}{\sqrt{d_y^2 + d_z^2}}\right)
\\
\\
{\rm yaw} &= \arctan \left(\frac{d_z}{d_x}\right)
\end{align*} 
$$

### `onMouseButton` function

To stamp cows, need to set clicked position and compare to dropped position so that when two are different means the vertical drag occured and same for stamping.

```python
if button == glfw.MOUSE_BUTTON_LEFT:
    if state == GLFW_DOWN:
        print(isDrag)
        if isDrag==0:
            isDrag=H_DRAG;
        
        isDrag=V_DRAG;

        clickPos = (x,y);
        print( "Left mouse down-click at %d %d\n" % (x,y))
        # start vertical dragging
    elif state == GLFW_UP and isDrag!=0:
        # when cow placed six times
        print((x, y) == clickPos)
        if cowCount == 0:
            isDrag=H_DRAG;
            cowCount += 1;
        elif (x,y) != clickPos:
            # v drag happend
            isDrag=H_DRAG;
        elif isDrag!=0:
            if (cowCount > C_MAX):
                isDrag=0;
                # cowCount = 0;
            else:
                cows[cowCount - 1] = cow2wld.copy();
                print(cowCount, cow2wld)
                cowCount += 1;
                isDrag=H_DRAG;
        print( "Left mouse up\n");
```

### `onMouseDrag` function
To implement vertical dragging without interfering horizontal dragging, this function had to be modified.

So for the `V_DRAG` case, I calculated ray that intersecting the plane with normal vector $(1,0,0)^\top$, and restricted vector components except for y component so that the grabbed cow can move only along to the vertical line (along through the y-axis).

And also capture the `pickInfo` not to be the vertically-moved point ignored in later `H_DRAG` case.

```python
if  isDrag==V_DRAG:
    # vertical dragging
    # TODO:
    # create a dragging plane perpendicular to the ray direction, 
    # and test intersection with the screen ray.
    if cursorOnCowBoundingBox:
        ray=screenCoordToRay(window, x, y);
        pp=pickInfo;
        p=Plane(np.array((1,0,0)), pp.cowPickPosition);

        c=ray.intersectsPlane(p);

        currentPos=ray.getPoint(c[1])
        currentPos[0], currentPos[2] = pp.cowPickPosition[0], pp.cowPickPosition[2]
        
        T=np.eye(4)
        setTranslation(T, currentPos-pp.cowPickPosition)
        cow2wld=T@pp.cowPickConfiguration;
    
        # pp.cowPickPosition = currentPos.copy()
        cowPickPosition=currentPos;
        cowPickLocalPos=transform(np.linalg.inv(cow2wld),cowPickPosition)

        pickInfo=PickInfo(c[1], cowPickPosition, cow2wld, cowPickLocalPos )
    print('vdrag')
```

This capturing trick can be also found in `H_DRAG` case.
