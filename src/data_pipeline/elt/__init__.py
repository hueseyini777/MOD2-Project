"""ELT variant of the same pipeline: load raw, then transform with SQL.

This package is entirely separate from the ETL implementation in the parent
package — extract.py, transform.py, load.py, and pipeline.py there are
untouched. Only extract.py is reused here, since downloading the raw files
is identical regardless of whether the rest of the pipeline is ETL or ELT.
"""
