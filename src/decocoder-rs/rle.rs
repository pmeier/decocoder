use numpy::PyReadwriteArray2;

pub fn fill(a: &mut PyReadwriteArray2<u8>, counts: &[usize]) {
    // counts comes on column major (Fortran-style) order, but array in row major (C-Style) order
    let [num_rows, num_cols] = <[usize; 2]>::try_from(a.shape()).ok().unwrap();
    let cmi_to_rmi = |i: usize| (i % num_rows) * num_cols + i / num_rows;

    let data = a.as_slice_mut().expect("Input array is not contiguous!");
    let mut offset: usize = 0;
    for (i, count) in counts.iter().enumerate() {
        if i % 2 == 1 {
            for idx in (offset..offset + count).map(cmi_to_rmi) {
                data[idx] = 255;
            }
        }
        offset += count;
    }
}
