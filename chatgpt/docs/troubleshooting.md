# 🛠️ Troubleshooting & Tips

Common issues a new learner might hit and how to debug them.

---

## Containers Don't Start

- Run:

  ```bash
  docker-compose ps
  docker-compose logs <service-name>
  ```

- Look for:
  - `ModuleNotFoundError` in Python containers → reinstall dependencies.
  - `Could not connect to endpoint` in Java worker → LocalStack or Chroma service may not be ready.

---

## LocalStack S3 Errors

Symptoms:

- `NoSuchBucket` or `AccessDenied` errors.

Causes & Fixes:

- Bucket may not exist yet:
  - The Unstructured and Java worker services both try to ensure the bucket exists.
  - Ensure `S3_BUCKET_NAME=documents` is consistent across services.
- Wrong endpoint:
  - Inside Docker: use `http://localstack:4566`
  - On host: use `http://localhost:4566`

---

## Chroma Service Issues

If `/embed` fails:

- Check `docker-compose logs chroma-service`.
- Ensure the volume directory (`/data/chroma`) is writable.
- Verify `chromadb` installed correctly in the container.

If `/query` returns no results:

- Verify the Java worker is successfully sending embeds:
  - Look for "Chroma response" log lines in `java-worker` logs.
- Make sure you actually uploaded documents after starting the stack.

---

## Java Worker Issues

If no embedding calls are happening:

- Check logs:

  ```bash
  docker-compose logs java-worker
  ```

- Things to confirm:
  - Does `listObjectsV2` show any objects?
  - Are `.txt` keys being found?
  - Are errors printed when sending to Chroma?

You can also temporarily lower the polling delay in `@Scheduled(fixedDelay = 10_000)`.

---

## General Tips

- Make small changes and rebuild:

  ```bash
  docker-compose up --build
  ```

- Use `curl` or tools like Postman to test:
  - `POST http://localhost:9000/embed`
  - `POST http://localhost:9000/query`

- Add more logging as you learn; logs are your best friend in distributed systems.

---

This troubleshooting guide is meant to help a **new learner** get unstuck while experimenting with this RAG pipeline.
