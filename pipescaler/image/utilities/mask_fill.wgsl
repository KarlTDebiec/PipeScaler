// Copyright 2026 Karl T Debiec. All rights reserved. This software may be
// modified and distributed under the terms of the BSD license. See the LICENSE
// file for details.
//
// Each round dispatches reset, count_neighbors, and fill in order. Dispatch
// boundaries synchronize all workgroups. Count computes colors before fill
// changes any mask or pixel, preserving the previous-round neighborhood.
// Pixels pack R/L in bits 0..7, G in 8..15, and B in 16..23. Candidates store
// the averaged color in those bits and the unmasked-neighbor count in 24..31.
// Params contains width and height. Python replaces WGX and WGY on load.

@group(0) @binding(0)
var<storage, read_write> pixels: array<u32>;
@group(0) @binding(1)
var<storage, read_write> mask: array<u32>;
@group(0) @binding(2)
var<storage, read_write> candidates: array<u32>;
@group(0) @binding(3)
var<storage, read_write> maximum: atomic<u32>;
@group(0) @binding(4)
var<storage, read> params: array<u32>;

var<workgroup> group_maximum: atomic<u32>;

@compute @workgroup_size(1)
fn reset() {
    atomicStore(&maximum, 0u);
}

@compute @workgroup_size(WGX, WGY)
fn count_neighbors(
    @builtin(global_invocation_id) gid: vec3<u32>,
    @builtin(local_invocation_index) local_index: u32,
) {
    if local_index == 0u {
        atomicStore(&group_maximum, 0u);
    }
    workgroupBarrier();

    let width = params[0];
    let height = params[1];
    if gid.x < width && gid.y < height {
        let index = gid.y * width + gid.x;
        if mask[index] != 0u {
            var count = 0u;
            var color = vec3<u32>(0u);
            let y_start = max(0, i32(gid.y) - 1);
            let y_end = min(i32(height) - 1, i32(gid.y) + 1);
            let x_start = max(0, i32(gid.x) - 1);
            let x_end = min(i32(width) - 1, i32(gid.x) + 1);
            for(var y = y_start; y <= y_end; y++) {
                for(var x = x_start; x <= x_end; x++) {
                    let neighbor = u32(y) * width + u32(x);
                    if mask[neighbor] == 0u {
                        let pixel = pixels[neighbor];
                        color += vec3<u32>(
                                pixel & 255u,
                                (pixel >> 8u) & 255u,
                                (pixel >> 16u) & 255u,
                            );
                        count++;
                    }
                }
            }
            var candidate = 0u;
            if count > 0u {
                color /= vec3<u32>(count);
                candidate = color.r | (color.g << 8u) | (color.b << 16u)
                    | (count << 24u);
                atomicMax(&group_maximum, count);
            }
            candidates[index] = candidate;
        }
    }
    workgroupBarrier();
    if local_index == 0u {
        let count = atomicLoad(&group_maximum);
        if count > 0u {
            atomicMax(&maximum, count);
        }
    }
}

@compute @workgroup_size(WGX, WGY)
fn fill(@builtin(global_invocation_id) gid: vec3<u32>) {
    let width = params[0];
    let height = params[1];
    if gid.x >= width || gid.y >= height {
        return;
    }
    let index = gid.y * width + gid.x;
    let count = atomicLoad(&maximum);
    if count > 0u && mask[index] != 0u && (candidates[index] >> 24u) == count {
        pixels[index] = candidates[index] & 0x00ffffffu;
        mask[index] = 0u;
    }
}
