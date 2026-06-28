# Centralized, immutable Scnehaux Architecture Linter image.
#
# Downstream repositories run this image against their docs directory to enforce
# governance WITHOUT maintaining a local (tamperable) copy of the engine.
# See GDC-001 §4.1 "Downstream Integration (Remote Execution)", Option B.
#
#   docker run --rm -v "$PWD:/docs" ghcr.io/scnehaux/gdc-linter:latest --target /docs
#
FROM python:3.13-slim

WORKDIR /linter

# Install pinned dependencies first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the engine and the authoritative rulesets (the rules resolve relative to
# linter.py via SCRIPT_DIR, so the directory layout must be preserved).
COPY linter.py .
COPY validators/ ./validators/
COPY 00-governance/rules/ ./00-governance/rules/

# Documents are mounted here by the caller.
WORKDIR /docs
RUN useradd -m linteruser && \
    chown -R linteruser:linteruser /linter && \
    chown -R linteruser:linteruser /docs

USER linteruser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import validators; print('ok')" || exit 1

ENTRYPOINT ["python", "/linter/linter.py"]
CMD ["--target", "/docs"]
