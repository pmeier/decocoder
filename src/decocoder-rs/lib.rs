use numpy::pyo3::Python;
use numpy::PyReadwriteArray2;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

mod polygons;
mod rle;

#[pyfunction]
#[pyo3(text_signature = "(mask: np.ndarray, counts: List[int])")]
fn decode_rle(mut mask: PyReadwriteArray2<u8>, counts: Vec<usize>) -> PyResult<()> {
    let total_count: usize = counts.iter().sum();
    if total_count != mask.len() {
        return Err(PyRuntimeError::new_err(format!(
            "Sum of all counts doesn't match number of elements in array: {total_count} != {len}",
            len = mask.len()
        )));
    }

    rle::fill(&mut mask, &counts);
    Ok(())
}

#[pyfunction]
#[pyo3(text_signature = "(mask: np.ndarray, polygons: List[List[float]])")]
fn decode_polygons(mut mask: PyReadwriteArray2<u8>, polygons: Vec<Vec<f32>>) -> PyResult<()> {
    let vertices: Vec<Vec<polygons::Vertex>> = polygons
        .into_iter()
        .enumerate()
        .map(|(idx, polygon)| {
            if polygon.len() % 2 == 1 {
                // FIXME
                Err(PyRuntimeError::new_err(format!(
                    "Polygons should XXX, but polygon at index {idx} has {len} entries",
                    len = polygon.len()
                )))
            } else {
                // FIXME remove else clause here and and also fail in case vertex is outside of image; round down exact edge matches
                Ok({
                    let mut polygon_vertices: Vec<polygons::Vertex> = polygon
                        .chunks(2)
                        .map(polygons::Vertex::from_adjacent_coordinates)
                        .collect();
                    // make sure that polygon is closed
                    polygon_vertices.push(polygon_vertices[0]);
                    polygon_vertices
                })
            }
        })
        .collect::<Result<_, _>>()?;

    polygons::fill(&mut mask, &vertices);
    Ok(())
}

#[pymodule]
fn _rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(decode_rle, m)?)?;
    m.add_function(wrap_pyfunction!(decode_polygons, m)?)?;
    Ok(())
}
