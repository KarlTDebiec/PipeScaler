// Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be
// modified and distributed under the terms of the BSD license. See the LICENSE
// file for details.
//
// Basic and local palette match compute shader
//
// Conventions for this file:
// - This shader is loaded from Python and templated by replacing `WGX` and `WGY`
//   with integer workgroup sizes before dispatch.
// - Pixel buffers are channel-interleaved and flattened in row-major order.
// - `params` layout:
//   [0]=fit_height, [1]=fit_width, [2]=ref_height, [3]=ref_width,
//   [4]=local_range, [5]=channels (1 for L, 3 for RGB)
// - A zero local_range selects the full ordered reference palette
// - Positive local_range selects a validated local reference neighborhood

// Input/output storage buffers for compute pass.
@group(0) @binding(0)
var<storage, read> fit_pixels: array<u32>;
@group(0) @binding(1)
var<storage, read> ref_pixels: array<u32>;
@group(0) @binding(2)
var<storage, read> params: array<u32>;
@group(0) @binding(3)
var<storage, read_write> output_pixels: array<u32>;

// Exact squared weighted RGB distance multiplied by 512
// Byte channels bound this value below 332667901, safely within u32
// Integer comparisons preserve near ties without float32 rounding
fn weighted_distance(
    fit_r_u: u32,
    fit_g_u: u32,
    fit_b_u: u32,
    ref_r_u: u32,
    ref_g_u: u32,
    ref_b_u: u32,
) -> u32 {
    let rsum = fit_r_u + ref_r_u;
    let dr = i32(fit_r_u) - i32(ref_r_u);
    let dg = i32(fit_g_u) - i32(ref_g_u);
    let db = i32(fit_b_u) - i32(ref_b_u);
    return (1024u + rsum) * u32(dr * dr) + 2048u * u32(dg * dg)
        + (1534u - rsum) * u32(db * db);
}

@compute @workgroup_size(WGX, WGY, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    let fit_height: u32 = params[0];
    let fit_width: u32 = params[1];
    let ref_height: u32 = params[2];
    let ref_width: u32 = params[3];
    let local_range: i32 = i32(params[4]);
    let channels: u32 = params[5];

    let x = gid.x;
    let y = gid.y;
    if x >= fit_width || y >= fit_height {
        return;
    }

    // Current fit pixel.
    let fit_idx = (y * fit_width + x) * channels;
    let fit_r = fit_pixels[fit_idx];
    var fit_g = fit_r;
    var fit_b = fit_r;
    if channels == 3u {
        fit_g = fit_pixels[fit_idx + 1u];
        fit_b = fit_pixels[fit_idx + 2u];
    }

    var x_start = 0;
    var x_end = i32(ref_width) - 1;
    var y_start = 0;
    var y_end = i32(ref_height) - 1;
    if local_range > 0 {
        // Validated local geometry has the same integer scale on both axes
        let scale = fit_width / ref_width;
        let center_x = i32(x / scale);
        let center_y = i32(y / scale);
        x_start = max(0, center_x - local_range);
        x_end = min(i32(ref_width) - 1, center_x + local_range);
        y_start = max(0, center_y - local_range);
        y_end = min(i32(ref_height) - 1, center_y + local_range);
    }

    // Brute-force search within local window in reference image.
    var best_dist = 0xffffffffu;
    var best_r: u32 = fit_r;
    var best_g: u32 = fit_g;
    var best_b: u32 = fit_b;

    var ry = y_start;
    loop {
        if ry > y_end || best_dist == 0u {
            break;
        }
        var rx = x_start;
        loop {
            if rx > x_end || best_dist == 0u {
                break;
            }
            let ref_idx = (u32(ry) * ref_width + u32(rx)) * channels;
            let ref_r = ref_pixels[ref_idx];
            var ref_g = ref_r;
            var ref_b = ref_r;
            if channels == 3u {
                ref_g = ref_pixels[ref_idx + 1u];
                ref_b = ref_pixels[ref_idx + 2u];
            }

            var dist = 0u;
            if channels == 3u {
                dist = weighted_distance(fit_r, fit_g, fit_b, ref_r, ref_g, ref_b);
            } else {
                let d = i32(fit_r) - i32(ref_r);
                dist = u32(d * d);
            }

            if dist < best_dist {
                best_dist = dist;
                best_r = ref_r;
                best_g = ref_g;
                best_b = ref_b;
            }

            rx = rx + 1;
        }
        ry = ry + 1;
    }

    // Emit best-matching reference color for this fit pixel.
    output_pixels[fit_idx] = best_r;
    if channels == 3u {
        output_pixels[fit_idx + 1u] = best_g;
        output_pixels[fit_idx + 2u] = best_b;
    }
}
