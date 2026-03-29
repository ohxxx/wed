use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

fn to_py_error(err: crypto_core::CryptoError) -> PyErr {
    PyValueError::new_err(err.to_string())
}

#[pyfunction]
fn encrypt_text(passphrase: &str, plaintext: &str) -> PyResult<String> {
    crypto_core::encrypt_text(passphrase, plaintext).map_err(to_py_error)
}

#[pyfunction]
fn decrypt_text(passphrase: &str, token: &str) -> PyResult<String> {
    crypto_core::decrypt_text(passphrase, token).map_err(to_py_error)
}

#[pyfunction]
fn encrypt_json(py: Python<'_>, passphrase: &str, value: Py<PyAny>) -> PyResult<String> {
    let json = py.import_bound("json")?;
    let kwargs = PyDict::new_bound(py);
    kwargs.set_item("separators", (",", ":"))?;
    let plaintext: String = json
        .call_method("dumps", (value,), Some(&kwargs))?
        .extract()?;

    crypto_core::encrypt_text(passphrase, &plaintext).map_err(to_py_error)
}

#[pyfunction]
fn decrypt_json(py: Python<'_>, passphrase: &str, token: &str) -> PyResult<Py<PyAny>> {
    let plaintext = crypto_core::decrypt_text(passphrase, token).map_err(to_py_error)?;
    let json = py.import_bound("json")?;
    let value = json.call_method1("loads", (plaintext,))?;
    Ok(value.unbind())
}

#[pymodule]
fn wedpy(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(encrypt_text, module)?)?;
    module.add_function(wrap_pyfunction!(decrypt_text, module)?)?;
    module.add_function(wrap_pyfunction!(encrypt_json, module)?)?;
    module.add_function(wrap_pyfunction!(decrypt_json, module)?)?;
    Ok(())
}
