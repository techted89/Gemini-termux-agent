# Termux Installation Notes

The following Python packages were removed from `requirements-termux.txt` because they are either not compatible with Termux or require special installation procedures.

## `scikit-learn`

The `scikit-learn` package requires a compiler and several other dependencies. To install it on Termux, you can use the following command:

```bash
pkg install scikit-learn
```

## `torch`

The `torch` package is not available through `pip` on Termux. It can be installed using the `unstable-repo` package source:

```bash
pkg install unstable-repo
pkg install pytorch
```

## `sentence-transformers`

The `sentence-transformers` package depends on `torch`, so it must be installed after `torch` is installed.

```bash
pip install sentence-transformers
```
