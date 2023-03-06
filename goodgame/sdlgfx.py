import math
import ctypes
from sdl2 import *


AAlevels = 256
AAbits = 8
DEFAULT_ELLIPSE_OVERSCAN = 4


def pixel(renderer: SDL_Renderer, x: int, y: int) -> int:
    return SDL_RenderDrawPoint(renderer, x, y)


def pixelRGBA(renderer: SDL_Renderer, x: int, y: int, r: int, g: int, b: int, a: int) -> int:
    return SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
        SDL_SetRenderDrawColor(renderer, r, g, b, a) | \
        SDL_RenderDrawPoint(renderer, x, y)


def pixelRGBAWeight(renderer: SDL_Renderer, x: int, y: int, r: int, g: int, b: int, a: int, weight: int) -> int:
    ax = ((a * weight) >> 8)
    if ax > 255:
        a = 255
    else:
        a = ax & 0x000000ff
    return pixelRGBA(renderer, x, y, r, g, b, a)


def hline(renderer: SDL_Renderer, x1: int, x2: int, y: int) -> int:
    return SDL_RenderDrawLine(renderer, x1, y, x2, y)


def hlineRGBA(renderer: SDL_Renderer, x1: int, x2: int, y: int, r: int, g: int, b: int, a: int) -> int:
    return SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
        SDL_SetRenderDrawColor(renderer, r, g, b, a) | \
        SDL_RenderDrawLine(renderer, x1, y, x2, y)


def vline(renderer: SDL_Renderer, x: int, y1: int, y2: int) -> int:
    return SDL_RenderDrawLine(renderer, x, y1, x, y2)


def vlineRGBA(renderer: SDL_Renderer, x: int, y1: int, y2: int, r: int, g: int, b: int, a: int) -> int:
    return SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
        SDL_SetRenderDrawColor(renderer, r, g, b, a) | \
        SDL_RenderDrawLine(renderer, x, y1, x, y2)


def rectangleRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int) -> int:
    if x1 == x2:
        if y1 == y2:
            return pixelRGBA(renderer, x1, y1, r, g, b, a)
        else:
            return vlineRGBA(renderer, x1, y1, y2, r, g, b, a)
    elif y1 == y2:
        return hlineRGBA(renderer, x1, x2, y1, r, g, b, a)

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    return SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
        SDL_SetRenderDrawColor(renderer, r, g, b, a) | \
        SDL_RenderDrawRect(renderer, SDL_Rect(x1, y1, x2 - x1, y2 - y1))


def roundedRectangleRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, rad: int, r: int, g: int, b: int, a: int
) -> int:
    if not renderer or rad < 0:
        return -1

    if rad <= 1:
        return rectangleRGBA(renderer, x1, y1, x2, y2, r, g, b, a)
    elif x1 == x2:
        if y1 == y2:
            return pixelRGBA(renderer, x1, y1, r, g, b, a)
        else:
            return vlineRGBA(renderer, x1, y1, y2, r, g, b, a)
    elif y1 == y2:
        return hlineRGBA(renderer, x1, x2, y1, r, g, b, a)

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    w, h = x2 - x1, y2 - y1

    if rad * 2 > w:
        rad = w // 2
    if rad * 2 > h:
        rad = h // 2

    xx1 = x1 + rad
    xx2 = x2 - rad
    yy1 = y1 + rad
    yy2 = y2 - rad

    result = arcRGBA(renderer, xx1, yy1, rad, 180, 270, r, g, b, a) | \
             arcRGBA(renderer, xx2, yy1, rad, 270, 360, r, g, b, a) | \
             arcRGBA(renderer, xx1, yy2, rad, 90, 180, r, g, b, a) | \
             arcRGBA(renderer, xx2, yy2, rad, 0, 90, r, g, b, a)

    if xx1 <= xx2:
        result |= hlineRGBA(renderer, xx1, xx2, y1, r, g, b, a) | hlineRGBA(renderer, xx1, xx2, y2, r, g, b, a)
    if yy1 <= yy2:
        result |= vlineRGBA(renderer, x1, yy1, yy2, r, g, b, a) | vlineRGBA(renderer, x2, yy1, yy2, r, g, b, a)

    return result


def roundedBoxRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, rad: int, r: int, g: int, b: int, a: int
) -> int:
    if not renderer or rad < 0:
        return -1

    if rad <= 1:
        return boxRGBA(renderer, x1, y1, x2, y2, r, g, b, a)
    elif x1 == x2:
        if y1 == y2:
            return pixelRGBA(renderer, x1, y1, r, g, b, a)
        else:
            return vlineRGBA(renderer, x1, y1, y2, r, g, b, a)
    elif y1 == y2:
        return hlineRGBA(renderer, x1, x2, y1, r, g, b, a)

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    w, h = x2 - x1 + 1, y2 - y1 + 1
    r2 = rad + rad

    if r2 > w:
        rad = w // 2
        r2 = rad + rad
    if r2 > h:
        rad = h // 2

    x = x1 + rad
    y = y1 + rad
    dx = x2 - x1 - rad - rad
    dy = y2 - y1 - rad - rad

    result = SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
             SDL_SetRenderDrawColor(renderer, r, g, b, a)

    cx, cy = 0, rad
    ocx = ocy = 0xffff
    df = 1 - rad
    d_e = 3
    d_se = -2 * rad + 5
    first = True
    while cx <= cy or first:
        first = False
        xpcx = x + cx
        xmcx = x - cx
        xpcy = x + cy
        xmcy = x - cy
        if not ocy == cy:
            if cy > 0:
                ypcy = y + cy
                ymcy = y - cy
                result |= hline(renderer, xmcx, xpcx + dx, ypcy + dy)
                result |= hline(renderer, xmcx, xpcx + dx, ymcy)
            else:
                result |= hline(renderer, xmcx, xpcx + dx, y)
            ocy = cy
        if not ocx == cx:
            if cx > 0:
                ypcx = y + cx
                ymcx = y - cx
                result |= hline(renderer, xmcy, xpcy + dx, ymcx)
                result |= hline(renderer, xmcy, xpcy + dx, ypcx + dy)
            else:
                result |= hline(renderer, xmcy, xpcy + dx, y)
            ocx = cx
        if df < 0:
            df += d_e
            d_e += 2
            d_se += 2
        else:
            df += d_se
            d_e += 2
            d_se += 4
            cy -= 1
        cx += 1

    if dx > 0 and dy > 0:
        result |= boxRGBA(renderer, x1, y1 + rad + 1, x2, y2 - rad, r, g, b, a)

    return result


def boxRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int) -> int:
    if x1 == x2:
        if y1 == y2:
            return pixelRGBA(renderer, x1, y1, r, g, b, a)
        else:
            return vlineRGBA(renderer, x1, y1, y2, r, g, b, a)
    elif y1 == y2:
        return hlineRGBA(renderer, x1, x2, y1, r, g, b, a)

    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    return SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
        SDL_SetRenderDrawColor(renderer, r, g, b, a) | \
        SDL_RenderFillRect(renderer, SDL_Rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1))


def line(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int) -> int:
    return SDL_RenderDrawLine(renderer, x1, y1, x2, y2)


def lineRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int) -> int:
    return SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
        SDL_SetRenderDrawColor(renderer, r, g, b, a) | \
        SDL_RenderDrawLine(renderer, x1, y1, x2, y2)


def _aalineRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int, draw_endpoint: int
) -> int:
    xx0 = x1
    yy0 = y1
    xx1 = x2
    yy1 = y2
    if yy0 > yy1:
        tmp = yy0
        yy0 = yy1
        yy1 = tmp
        tmp = xx0
        xx0 = xx1
        xx1 = tmp
    dx = xx1 - xx0
    dy = yy1 - yy0
    if dx >= 0:
        xdir = 1
    else:
        xdir = -1
        dx = -dx

    if dx == 0:
        if draw_endpoint:
            return vlineRGBA(renderer, x1, y1, y2, r, g, b, a)
        else:
            if dy > 0:
                return vlineRGBA(renderer, x1, yy0, yy0 + dy, r, g, b, a)
            else:
                return pixelRGBA(renderer, x1, y1, r, g, b, a)
    elif dy == 0:
        if draw_endpoint:
            return hlineRGBA(renderer, x1, x2, y1, r, g, b, a)
        else:
            if dy > 0:
                return vlineRGBA(renderer, xx0, xx0 + xdir * dx, y1, r, g, b, a)
            else:
                return pixelRGBA(renderer, x1, y1, r, g, b, a)
    elif dx == dy and draw_endpoint:
        return lineRGBA(renderer, x1, y1, x2, y2, r, g, b, a)

    erracc = 0
    intshift = 32 - AAbits
    wgtcompmask = AAlevels - 1
    result = pixelRGBA(renderer, x1, y1, r, g, b, a)
    if dy > dx:
        erradj = ((dx << 16) // dy) << 16
        x0pxdir = xx0 + xdir
        while dy - 1:
            erracctmp = erracc
            erracc += erradj
            if erracc <= erracctmp:
                xx0 = x0pxdir
                x0pxdir += xdir
            yy0 += 1
            wgt = (erracc >> intshift) & 255
            result |= pixelRGBAWeight(renderer, xx0, yy0, r, g, b, a, 255 - wgt)
            result |= pixelRGBAWeight(renderer, x0pxdir, yy0, r, g, b, a, wgt)
    else:
        erradj = ((dy << 16) // dx) << 16
        y0p1 = yy0 + 1
        while dx - 1:
            erracctmp = erracc
            erracc += erradj
            if erracc <= erracctmp:
                yy0 = y0p1
                y0p1 += 1
        xx0 += xdir
        wgt = (erracc >> intshift) & 255
        result |= pixelRGBAWeight(renderer, xx0, yy0, r, g, b, a, 255 - wgt)
        result |= pixelRGBAWeight(renderer, xx0, y0p1, r, g, b, a, wgt)

    if draw_endpoint:
        result |= pixelRGBA(renderer, x2, y2, r, g, b, a)

    return result


def aalineRGBA(renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int) -> int:
    return _aalineRGBA(renderer, x1, y1, x2, y2, r, g, b, a, 1)


def circleRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, r: int, g: int, b: int, a: int) -> int:
    return ellipseRGBA(renderer, x, y, rad, rad, r, g, b, a)


def arcRGBA(
        renderer: SDL_Renderer, x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int
) -> int:
    if rad < 0:
        return -1
    if rad == 0:
        return pixelRGBA(renderer, x, y, r, g, b, a)

    start %= 360
    end %= 360
    while start < 0:
        start += 360
    while end < 0:
        end += 360
    start %= 360
    end %= 360
    startoct = start // 45
    endoct = end // 45
    _oct = startoct - 1
    drawoct = 0
    stopval_start = stopval_end = 0
    temp = 0.0

    first = True
    while not _oct == endoct or first:
        first = False
        _oct = (_oct + 1) % 8
        if _oct == startoct:
            dstart = float(start)
            if _oct == 0 or _oct == 3:
                temp = math.sin(dstart * math.pi / 180)
            elif _oct == 1 or _oct == 6:
                temp = math.cos(dstart * math.pi / 180)
            elif _oct == 2 or _oct == 5:
                temp = -math.cos(dstart * math.pi / 180)
            elif _oct == 4 or _oct == 7:
                temp = -math.sin(dstart * math.pi / 180)
            temp *= rad
            stopval_start = int(temp)
            if _oct % 2:
                drawoct |= 1 << _oct
            else:
                drawoct &= 255 - (1 << _oct)
        if _oct == endoct:
            dend = float(end)
            if _oct == 0 or _oct == 3:
                temp = math.sin(dend * math.pi / 180)
            elif _oct == 1 or _oct == 6:
                temp = math.cos(dend * math.pi / 180)
            elif _oct == 2 or _oct == 5:
                temp = -math.cos(dend * math.pi / 180)
            elif _oct == 4 or _oct == 7:
                temp = -math.sin(dend * math.pi / 180)
            temp *= rad
            stopval_end = int(temp)
            if startoct == endoct:
                if start > end:
                    drawoct = 255
                else:
                    drawoct &= 255 - (1 << _oct)
            elif _oct % 2:
                drawoct &= 255 - (1 << _oct)
            else:
                drawoct |= 1 << _oct
        elif not _oct == startoct:
            drawoct |= (1 << _oct)

    result = SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
             SDL_SetRenderDrawColor(renderer, r, g, b, a)

    cx, cy = 0, rad
    df = 1 - rad
    d_e = 3
    d_se = -2 * rad + 5
    first = True
    while cx <= cy or first:
        first = False
        ypcy = y + cy
        ymcy = y - cy
        if cx > 0:
            xpcx = x + cx
            xmcx = x - cx
            if drawoct & 4:
                result |= pixel(renderer, xmcx, ypcy)
            if drawoct & 2:
                result |= pixel(renderer, xpcx, ypcy)
            if drawoct & 32:
                result |= pixel(renderer, xmcx, ymcy)
            if drawoct & 64:
                result |= pixel(renderer, xpcx, ymcy)
        else:
            if drawoct & 96:
                result |= pixel(renderer, x, ymcy)
            if drawoct & 6:
                result |= pixel(renderer, x, ypcy)
        xpcy = x + cy
        xmcy = x - cy

        if cx > 0 and not cx == cy:
            ypcx = y + cx
            ymcx = y - cx
            if drawoct & 8:
                result |= pixel(renderer, xmcy, ypcx)
            if drawoct & 1:
                result |= pixel(renderer, xpcy, ypcx)
            if drawoct & 16:
                result |= pixel(renderer, xmcy, ymcx)
            if drawoct & 128:
                result |= pixel(renderer, xpcy, ymcx)
        elif cx == 0:
            if drawoct & 24:
                result |= pixel(renderer, xmcy, y)
            if drawoct & 129:
                result |= pixel(renderer, xpcy, y)

        if stopval_start == cx:
            if drawoct & (1 << startoct):
                drawoct &= 255 - (1 << startoct)
            else:
                drawoct |= (1 << startoct)
        if stopval_end == cx:
            if drawoct & (1 << endoct):
                drawoct &= 255 - (1 << endoct)
            else:
                drawoct |= (1 << endoct)

        if df < 0:
            df += d_e
            d_e += 2
            d_se += 2
        else:
            df += d_se
            d_e += 2
            d_se += 4
            cy -= 1
        cx += 1

    return result


def aacircleRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, r: int, b: int, g: int, a: int) -> int:
    return aaellipseRGBA(renderer, x, y, rad, rad, r, g, b, a)


def _drawQuadrants(renderer: SDL_Renderer, x: int, y: int, dx: int, dy: int, _f: int) -> int:
    if dx == 0:
        if dy == 0:
            result = pixel(renderer, x, y)
        else:
            ypdy = y + dy
            ymdy = y - dy
            if _f:
                result = vline(renderer, x, ymdy, ypdy)
            else:
                result = pixel(renderer, x, ypdy) | pixel(renderer, x, ymdy)
    else:
        xpdx = x + dx
        xmdx = x - dx
        ypdy = y + dy
        ymdy = y - dy
        if _f:
            result = vline(renderer, xpdx, ymdy, ypdy) | vline(renderer, xmdx, ymdy, ypdy)
        else:
            result = pixel(renderer, xpdx, ypdy) | pixel(renderer, xmdx, ypdy) | \
                     pixel(renderer, xpdx, ymdy) | pixel(renderer, xmdx, ymdy)
    return result


def _ellipseRGBA(
        renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int, _f: int
) -> int:
    if rx < 0 or ry < 0:
        return -1
    result = SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
             SDL_SetRenderDrawColor(renderer, r, g, b, a)
    if rx == 0:
        if ry == 0:
            return pixel(renderer, x, y)
        else:
            return vline(renderer, x, y - ry, y + ry)
    elif ry == 0:
        return hline(renderer, x - rx, x + rx, y)

    rxi, ryi = rx, ry
    if rxi >= 512 or ryi >= 512:
        ellipseOverscan = DEFAULT_ELLIPSE_OVERSCAN // 4
    elif rxi >= 256 or ryi >= 256:
        ellipseOverscan = DEFAULT_ELLIPSE_OVERSCAN // 2
    else:
        ellipseOverscan = DEFAULT_ELLIPSE_OVERSCAN
    oldX = scrX = 0
    oldY = scrY = ryi
    result |= _drawQuadrants(renderer, x, y, 0, ry, _f)

    rxi *= ellipseOverscan
    ryi *= ellipseOverscan
    rx2 = rxi * rxi
    rx22 = rx2 + rx2
    ry2 = ryi * ryi
    ry22 = ry2 + ry2
    curX = 0
    curY = ryi
    deltaX = 0
    deltaY = rx22 * curY
    _error = ry2 - rx2 * ryi + rx2 // 4
    while deltaX <= deltaY:
        curX += 1
        deltaX += ry22
        _error += deltaX + ry2
        if _error > 0:
            curY -= 1
            deltaY -= rx22
            _error -= deltaY
        scrX = curX // ellipseOverscan
        scrY = curY // ellipseOverscan
        if (not scrX == oldX and scrY == oldY) or (not scrX == oldX and not scrY == oldY):
            result |= _drawQuadrants(renderer, x, y, scrX, scrY, _f)
            oldX = scrX
            oldY = scrY

    if curY > 0:
        curXp1 = curX + 1
        curYm1 = curY - 1
        _error = ry2 * curX * curXp1 + ((ry2 + 3) // 4) + rx2 * curYm1 * curYm1 - rx2 * ry2
        while curY > 0:
            curY -= 1
            deltaY -= rx22
            _error += rx2
            _error -= deltaY
            if _error <= 0:
                curX += 1
                deltaX += ry22
                _error += deltaX
            scrX = curX // ellipseOverscan
            scrY = curY // ellipseOverscan
            if (not scrX == oldX and scrY == oldY) or (not scrX == oldX and not scrY == oldY):
                oldY -= 1
                while oldY >= scrY:
                    result |= _drawQuadrants(renderer, x, y, scrX, oldY, _f)
                    if _f:
                        oldY = scrY - 1
                    oldY -= 1
                oldX = scrX
                oldY = scrY
        if not _f:
            oldY -= 1
            while oldY >= 0:
                result |= _drawQuadrants(renderer, x, y, scrX, oldY, _f)
                oldY -= 1

    return result


def ellipseRGBA(renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int) -> int:
    return _ellipseRGBA(renderer, x, y, rx, ry, r, g, b, a, 0)


def filledCircleRGBA(renderer: SDL_Renderer, x: int, y: int, rad: int, r: int, g: int, b: int, a: int) -> int:
    return _ellipseRGBA(renderer, x, y, rad, rad, r, g, b, a, 1)


def aaellipseRGBA(renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int) -> int:
    if rx < 0 or ry < 0:
        return -1
    if rx == 0:
        if ry == 0:
            return pixel(renderer, x, y)
        else:
            return vline(renderer, x, y - ry, y + ry)
    elif ry == 0:
        return hline(renderer, x - rx, x + rx, y)
    a2 = rx * rx
    b2 = ry * ry
    ds = 2 * a2
    dt = 2 * b2
    xc2 = 2 * x
    yc2 = 2 * y
    sab = math.sqrt(a2 + b2)
    od = round(sab * 0.01) + 1
    dxt = round(a2 / sab) + od
    t = 0
    s = -2 * a2 * ry
    d = 0
    xp = x
    yp = y - ry
    result = SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE if a == 255 else SDL_BLENDMODE_BLEND) | \
             pixelRGBA(renderer, xp, yp, r, g, b, a) | pixelRGBA(renderer, xc2 - xp, yp, r, g, b, a) | \
             pixelRGBA(renderer, xp, yc2 - yp, r, g, b, a) | pixelRGBA(renderer, xc2 - xp, yc2 - yp, r, g, b, a)
    for _i in range(dxt):
        i = _i + 1
        xp -= 1
        d += t - b2
        if d >= 0:
            ys = yp - 1
        elif d - s - a2 > 0:
            if 2 * d - s - a2 >= 0:
                ys = yp + 1
            else:
                ys = yp
                yp += 1
                d -= s + a2
                s += ds
        else:
            yp += 1
            ys = yp + 1
            d -= s + a2
            s += ds
        t -= dt
        if s:
            cp = abs(d) / abs(s)
            if cp > 1.0:
                cp = 1.0
        else:
            cp = 1.0
        weight = int(cp * 255)
        iweight = 255 - weight
        xx = xc2 - xp
        result |= pixelRGBAWeight(renderer, xp, yp, r, g, b, a, iweight)
        result |= pixelRGBAWeight(renderer, xx, yp, r, g, b, a, iweight)
        result |= pixelRGBAWeight(renderer, xp, ys, r, g, b, a, weight)
        result |= pixelRGBAWeight(renderer, xx, ys, r, g, b, a, weight)
        yy = yc2 - yp
        result |= pixelRGBAWeight(renderer, xp, yy, r, g, b, a, iweight)
        result |= pixelRGBAWeight(renderer, xx, yy, r, g, b, a, iweight)
        yy = yc2 - ys
        result |= pixelRGBAWeight(renderer, xp, yy, r, g, b, a, weight)
        result |= pixelRGBAWeight(renderer, xx, yy, r, g, b, a, weight)
    dyt = round(b2 / sab) + od
    for _i in range(dxt):
        i = _i + 1
        yp += 1
        d += s + a2
        if d <= 0:
            xs = xp + 1
        elif d + t - b2 < 0:
            if 2 * d + t - b2 <= 0:
                xs = xp - 1
            else:
                xs = xp
                xp -= 1
                d += t - b2
                t -= dt
        else:
            xp -= 1
            xs = xp - 1
            d += t - b2
            t -= dt
        s += ds
        if t:
            cp = abs(d) / abs(t)
            if cp > 1.0:
                cp = 1.0
        else:
            cp = 1.0
        weight = int(cp * 255)
        iweight = 255 - weight
        xx = xc2 - xp
        yy = yc2 - yp
        result |= pixelRGBAWeight(renderer, xp, yp, r, g, b, a, iweight)
        result |= pixelRGBAWeight(renderer, xx, yp, r, g, b, a, iweight)
        result |= pixelRGBAWeight(renderer, xp, yy, r, g, b, a, iweight)
        result |= pixelRGBAWeight(renderer, xx, yy, r, g, b, a, iweight)
        xx = xc2 - xs
        result |= pixelRGBAWeight(renderer, xs, yp, r, g, b, a, weight)
        result |= pixelRGBAWeight(renderer, xx, yp, r, g, b, a, weight)
        result |= pixelRGBAWeight(renderer, xs, yy, r, g, b, a, weight)
        result |= pixelRGBAWeight(renderer, xx, yy, r, g, b, a, weight)

    return result


def filledEllipseRGBA(renderer: SDL_Renderer, x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int) -> int:
    return _ellipseRGBA(renderer, x, y, rx, ry, r, g, b, a, 1)


def _pieRGBA(
        renderer: SDL_Renderer, x: int, y: int, rad: int,
        start: int, end: int, r: int, g: int, b: int, a: int, filled: int
) -> int:
    # TODO
    return -1


def pieRGBA(
        renderer: SDL_Renderer, x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int
) -> int:
    return _pieRGBA(renderer, x, y, rad, start, end, r, g, b, a, 0)


def filledPieRGBA(
        renderer: SDL_Renderer, x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int
) -> int:
    return _pieRGBA(renderer, x, y, rad, start, end, r, g, b, a, 1)


def trigonRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, r: int, g: int, b: int, a: int
) -> int:
    return polygonRGBA(renderer, (ctypes.c_int16 * 3)(x1, x2, x3), (ctypes.c_int16 * 3)(y1, y2, y3), 3, r, g, b, a)


def aatrigonRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, r: int, g: int, b: int, a: int
) -> int:
    return aapolygonRGBA(renderer, (ctypes.c_int16 * 3)(x1, x2, x3), (ctypes.c_int16 * 3)(y1, y2, y3), 3, r, g, b, a)


def filledTrigonRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, r: int, g: int, b: int, a: int
) -> int:
    return filledPolygonRGBA(renderer, (ctypes.c_int16 * 3)(x1, x2, x3), (ctypes.c_int16 * 3)(y1, y2, y3), 3, r, g, b, a)


def polygon(renderer: SDL_Renderer, vx: any, vy: any, n: int) -> int:
    # TODO
    return -1


def polygonRGBA(renderer: SDL_Renderer, vx: any, vy: any, n: int, r: int, g: int, b: int, a: int) -> int:
    # TODO
    return -1


def aapolygonRGBA(renderer: SDL_Renderer, vx: any, vy: any, n: int, r: int, g: int, b: int, a: int) -> int:
    # TODO
    return -1


def filledPolygonRGBAMT(
        renderer: SDL_Renderer, vx: any, vy: any, n: int,
        r: int, g: int, b: int, a: int, polyInts: any, polyAllocated: any
) -> int:
    # TODO
    return -1


def filledPolygonRGBA(renderer: SDL_Renderer, vx: any, vy: any, n: int, r: int, g: int, b: int, a: int) -> int:
    return filledPolygonRGBAMT(renderer, vx, vy, n, r, g, b, a, None, None)


def _evaluateBezier(data: any, ndata: int, t: float) -> int:
    # TODO
    return -1


def bezierRGBA(renderer: SDL_Renderer, vx: any, vy: any, n: int, s: int, r: int, g: int, b: int, a: int) -> int:
    # TODO
    return -1


def thickLineRGBA(
        renderer: SDL_Renderer, x1: int, y1: int, x2: int, y2: int, width: int, r: int, g: int, b: int, a: int
) -> int:
    if not renderer or width < 1:
        return -1
    if x1 == x2 and y1 == y2:
        wh = width // 2
        return boxRGBA(renderer, x1 - wh, y1 - wh, x2 + width, y2 + width, r, g, b, a)
    if width == 1:
        return lineRGBA(renderer, x1, y1, x2, y2, r, g, b, a)
    dx = x2 - x1
    dy = y2 - y1
    _l = math.sqrt(dx * dx + dy * dy)
    ang = math.atan2(dx, dy)
    adj = 0.1 + 0.9 * abs(math.cos(2.0 * ang))
    wl2 = (width - adj) / (2.0 * _l)
    nx = dx * wl2
    ny = dy * wl2
    return filledPolygonRGBA(
        renderer, [x1 + ny, x1 - ny, x2 - ny, x2 + ny], [y1 - nx, y1 + nx, y2 + nx, y2 - nx], 4, r, g, b, a
    )
