import array

from arcade import gl
from arcade.color import WHITE
from arcade.math import rotate_point
from arcade.sprite import BasicSprite
from arcade.texture import Texture
from arcade.types import LBWH, LRBT, RGBA255, XYWH, Color, PointList, Rect
from arcade.window_commands import get_window

from .helpers import _generic_draw_line_strip


def draw_texture_rect(
    texture: Texture,
    rect: Rect,
    *,
    color: Color = WHITE,
    angle=0.0,
    blend=True,
    alpha=1.0,
    pixelated=False,
) -> None:
    """
    Draw a texture on a rectangle.

    :param texture: identifier of texture returned from load_texture() call
    :param rect: Rectangle to draw the texture on.
    :param color: Color of the texture. Defaults to white.
    :param angle: Rotation of the texture in degrees. Defaults to zero.
    :param blend: If True, enable alpha blending. Defaults to True.
    :param alpha: Transparency of image. 0.0 is fully transparent, 1.0 (default) is visible.
    """
    ctx = get_window().ctx

    if blend:
        ctx.enable(ctx.BLEND)
    else:
        ctx.disable(ctx.BLEND)

    atlas = ctx.default_atlas

    texture_id, _ = ctx.default_atlas.add(texture)
    if pixelated:
        atlas.texture.filter = gl.NEAREST, gl.NEAREST
    else:
        atlas.texture.filter = gl.LINEAR, gl.LINEAR

    atlas.texture.use(unit=0)
    atlas.use_uv_texture(unit=1)

    geometry = ctx.geometry_empty
    program = ctx.sprite_program_single
    program["pos"] = rect.center_x, rect.center_y, 0
    program["color"] = color.normalized
    program["size"] = rect.width, rect.height
    program["angle"] = angle
    program["texture_id"] = float(texture_id)
    program["spritelist_color"] = 1.0, 1.0, 1.0, alpha

    geometry.render(program, mode=gl.POINTS, vertices=1)

    if blend:
        ctx.disable(ctx.BLEND)


def draw_sprite(sprite: BasicSprite, *, blend: bool = True, alpha=1.0, pixelated=False) -> None:
    """
    Draw a sprite.

    :param sprite: The sprite to draw.
    """
    draw_texture_rect(
        sprite.texture,
        rect=XYWH(sprite.center_x, sprite.center_y, sprite.width, sprite.height),
        color=sprite.color,
        angle=sprite._angle,
        blend=blend,
        alpha=alpha,
        pixelated=pixelated,
    )


def draw_sprite_rect(
    sprite: BasicSprite, rect: Rect, *, blend: bool = True, alpha=1.0, pixelated=False
) -> None:
    """
    Draw a sprite.

    :param sprite: The sprite to draw.
    """
    draw_texture_rect(
        sprite.texture,
        rect=rect,
        color=sprite.color,
        angle=sprite._angle,
        blend=blend,
        alpha=alpha,
        pixelated=pixelated,
    )


def draw_lrbt_rectangle_outline(
    left: float,
    right: float,
    bottom: float,
    top: float,
    color: RGBA255,
    border_width: float = 1,
) -> None:
    """
    Draw a rectangle by specifying left, right, bottom and top edges.

    :param left: The x coordinate of the left edge of the rectangle.
    :param right: The x coordinate of the right edge of the rectangle.
    :param bottom: The y coordinate of the rectangle bottom.
    :param top: The y coordinate of the top of the rectangle.
    :param color: The color of the rectangle.
    :param border_width: The width of the border in pixels. Defaults to one.
    :Raises ValueError: Raised if left > right or top < bottom.

    """
    if left > right:
        raise ValueError("Left coordinate must be less than or equal to " "the right coordinate")

    if bottom > top:
        raise ValueError("Bottom coordinate must be less than or equal to " "the top coordinate")

    draw_rect_outline(LRBT(left, right, bottom, top), color, border_width)


def draw_lbwh_rectangle_outline(
    left: float,
    bottom: float,
    width: float,
    height: float,
    color: RGBA255,
    border_width: float = 1,
) -> None:
    """
    Draw a rectangle extending from bottom left to top right

    :param bottom_left_x: The x coordinate of the left edge of the rectangle.
    :param bottom_left_y: The y coordinate of the bottom of the rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param color: The color of the rectangle as an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param border_width: The width of the border in pixels. Defaults to one.
    """
    draw_rect_outline(LBWH(left, bottom, width, height), color, border_width)


def draw_lrbt_rectangle_filled(
    left: float, right: float, bottom: float, top: float, color: RGBA255
) -> None:
    """
    Draw a rectangle by specifying left, right, bottom and top edges.

    :param left: The x coordinate of the left edge of the rectangle.
    :param right: The x coordinate of the right edge of the rectangle.
    :param bottom: The y coordinate of the rectangle bottom.
    :param top: The y coordinate of the top of the rectangle.
    :param color: The color of the rectangle.
    :Raises ValueError: Raised if left > right or top < bottom.
    """
    if left > right:
        raise ValueError(
            f"Left coordinate {left} must be less than or equal to the right coordinate {right}"
        )

    if bottom > top:
        raise ValueError(
            f"Bottom coordinate {bottom} must be less than or equal to the top coordinate {top}"
        )

    draw_rect_filled(LRBT(left, right, bottom, top), color)


def draw_lbwh_rectangle_filled(
    left: float, bottom: float, width: float, height: float, color: RGBA255
) -> None:
    """
    Draw a filled rectangle extending from bottom left to top right

    :param left: The x coordinate of the left edge of the rectangle.
    :param bottom: The y coordinate of the bottom of the rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param color: The color of the rectangles an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    """
    draw_rect_filled(LBWH(left, bottom, width, height), color)


def draw_rect_outline(
    rect: Rect, color: RGBA255, border_width: float = 1, tilt_angle: float = 0
) -> None:
    """
    Draw a rectangle outline.

    :param rect: The rectangle to draw.
        a :py:class`~arcade.types.Rect` instance.
    :param color: The color of the rectangle.
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param border_width: width of the lines, in pixels.
    :param tilt_angle: rotation of the rectangle. Defaults to zero (clockwise).
    """

    HALF_BORDER = border_width / 2

    # fmt: off
    i_lb = rect.bottom_left.x  + HALF_BORDER, rect.bottom_left.y  + HALF_BORDER
    i_rb = rect.bottom_right.x - HALF_BORDER, rect.bottom_right.y + HALF_BORDER
    i_rt = rect.top_right.x    - HALF_BORDER, rect.top_right.y    - HALF_BORDER
    i_lt = rect.top_left.x     + HALF_BORDER, rect.top_left.y     - HALF_BORDER
    o_lb = rect.bottom_left.x  - HALF_BORDER, rect.bottom_left.y  - HALF_BORDER
    o_rb = rect.bottom_right.x + HALF_BORDER, rect.bottom_right.y - HALF_BORDER
    o_rt = rect.top_right.x    + HALF_BORDER, rect.top_right.y    + HALF_BORDER
    o_lt = rect.top_left.x     - HALF_BORDER, rect.top_right.y    + HALF_BORDER
    # fmt: on

    point_list: PointList = (o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt)

    if tilt_angle != 0:
        point_list_2 = []
        for point in point_list:
            new_point = rotate_point(point[0], point[1], rect.x, rect.y, tilt_angle)
            point_list_2.append(new_point)
        point_list = point_list_2

    _generic_draw_line_strip(point_list, color, gl.TRIANGLE_STRIP)


def draw_rect_filled(rect: Rect, color: RGBA255, tilt_angle: float = 0) -> None:
    """
    Draw a filled-in rectangle.

    :param rect: The rectangle to draw.
        a :py:class`~arcade.types.Rect` instance.
    :param color: The color of the rectangle as an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param tilt_angle: rotation of the rectangle (clockwise). Defaults to zero.
    """
    # Fail if we don't have a window, context, or right GL abstractions
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_rectangle_filled_unbuffered_program  # type: ignore
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer  # type: ignore

    # Validate & normalize to a pass the shader an RGBA float uniform
    color_normalized = Color.from_iterable(color).normalized

    ctx.enable(ctx.BLEND)

    # Pass data to the shader
    program["color"] = color_normalized
    program["shape"] = rect.width, rect.height, tilt_angle
    buffer.orphan()
    buffer.write(data=array.array("f", (rect.x, rect.y)))

    geometry.render(program, mode=ctx.POINTS, vertices=1)

    ctx.disable(ctx.BLEND)


# These might be "oddly specific" and also needs docstrings. Disabling or 3.0.0

# def draw_rect_outline_kwargs(
#     color: RGBA255 = WHITE, border_width: int = 1, tilt_angle: float = 0, **kwargs: AsFloat
# ) -> None:
#     rect = Rect.from_kwargs(**kwargs)
#     draw_rect_outline(rect, color, border_width, tilt_angle)


# def draw_rect_filled_kwargs(
#     color: RGBA255 = WHITE, tilt_angle: float = 0, **kwargs: AsFloat
# ) -> None:
#     rect = Rect.from_kwargs(**kwargs)
#     draw_rect_filled(rect, color, tilt_angle)
