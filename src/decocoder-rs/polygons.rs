use numpy::PyReadwriteArray2;

#[derive(Copy, Clone, Debug)]
pub struct Vertex {
    x: f32,
    y: f32,
}

impl Vertex {
    pub fn from_adjacent_coordinates(adjacent_coordinates: &[f32]) -> Vertex {
        debug_assert!(adjacent_coordinates.len() == 2);
        Vertex {
            x: adjacent_coordinates[0],
            y: adjacent_coordinates[1],
        }
    }
}

pub fn fill(mask: &mut PyReadwriteArray2<u8>, vertices: &[Vec<Vertex>]) {
    let edges: Vec<Edge> = vertices
        .iter()
        .flat_map(|polygon_vertices| {
            polygon_vertices
                .windows(2)
                .filter_map(Edge::maybe_from_adjacent_vertices)
        })
        .collect();

    // Having fewer than two edges cannot be a valid polygon. There are cases like this
    // in the official COCO data. For example, the annotation with ID 000000000918.
    // TODO: investigate if drawing nothing is ok in that case
    if edges.len() < 2 {
        return;
    }

    fill_with_scanlines(mask, edges);
}

#[derive(Debug)]
struct Edge {
    y_min: usize,
    y_max: usize,
    x_val: f32,
    inv_slope: f32,
}

impl Edge {
    fn maybe_from_adjacent_vertices(adjacent_vertices: &[Vertex]) -> Option<Edge> {
        debug_assert!(adjacent_vertices.len() == 2);
        let vertex_0 = &adjacent_vertices[0];
        let vertex_1 = &adjacent_vertices[1];

        let x_0: f32;
        let y_0: f32;
        let x_1: f32;
        let y_1: f32;
        if vertex_0.y < vertex_1.y {
            x_0 = vertex_0.x;
            y_0 = vertex_0.y;
            x_1 = vertex_1.x;
            y_1 = vertex_1.y;
        } else {
            x_0 = vertex_1.x;
            y_0 = vertex_1.y;
            x_1 = vertex_0.x;
            y_1 = vertex_0.y;
        }

        let y_min = y_0 as usize;
        let y_max = y_1 as usize;

        if y_min == y_max {
            return None;
        }

        let inv_slope = (x_1 - x_0) / (y_1 - y_0);
        let x_val = x_0 + inv_slope / 2.0;

        Some(Edge {
            y_min,
            y_max,
            x_val,
            inv_slope,
        })
    }

    fn update_x_val(&mut self) {
        self.x_val += self.inv_slope;
    }
}

fn fill_with_scanline(
    mask: &mut PyReadwriteArray2<u8>,
    edges: &[Edge],
    y_scan: usize,
    x_max: usize,
) {
    debug_assert!(edges.len() % 2 == 0);

    for adjacent_edges in edges.chunks(2) {
        let x_start = adjacent_edges[0].x_val as usize;
        let x_end = (adjacent_edges[1].x_val as usize).clamp(0, x_max);

        if x_start > x_end {
            *mask.get_mut((y_scan, x_end)).unwrap() = 255;
        } else {
            for x in x_start..=x_end {
                *mask.get_mut((y_scan, x)).unwrap() = 255;
            }
        }
    }
}

// https://www.cs.rit.edu/~icss571/filling/
fn fill_with_scanlines(mask: &mut PyReadwriteArray2<u8>, edges: Vec<Edge>) {
    let shape = mask.shape();
    let y_max = shape[0] - 1;
    let x_max = shape[1] - 1;

    let mut inactive_edges = edges;
    inactive_edges.sort_by_key(|edge| (edge.y_min, edge.x_val as usize, edge.inv_slope != 0.0));

    let mut y_scan = inactive_edges[0].y_min;

    let mut active_edges: Vec<Edge> = Vec::new();
    drain_filter_into(&mut inactive_edges, &mut active_edges, |edge| {
        edge.y_min == y_scan
    });

    let mut prev_processed_edges: Vec<Edge> = Vec::new();

    while !active_edges.is_empty() {
        fill_with_scanline(mask, &active_edges, y_scan, x_max);

        y_scan += 1;
        for edge in &mut active_edges {
            edge.update_x_val();
        }

        prev_processed_edges.clear();
        drain_filter_into(&mut active_edges, &mut prev_processed_edges, |edge| {
            edge.y_max == y_scan
        });

        drain_filter_into(&mut inactive_edges, &mut active_edges, |edge| {
            edge.y_min == y_scan
        });

        active_edges.sort_by_key(|edge| (edge.x_val as usize, edge.inv_slope != 0.0));
    }

    if y_scan < y_max {
        fill_with_scanline(mask, &prev_processed_edges, y_scan, x_max);
    }
}

fn drain_filter_into<T, P>(src: &mut Vec<T>, dst: &mut Vec<T>, predicate: P)
where
    P: Fn(&T) -> bool,
{
    let mut idx = 0;
    while idx < src.len() {
        if predicate(&src[idx]) {
            dst.push(src.remove(idx));
        } else {
            idx += 1;
        }
    }
}
