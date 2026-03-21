# HTTP Status Codes

HTTP status codes are three-digit numbers returned by a server in response to a
client's request. They are grouped into five classes based on the first digit.

## 1xx — Informational

These indicate that the request was received and the server is continuing to process it.

- **100 Continue** — The server received the request headers and the client should
  proceed to send the body. Used with `Expect: 100-continue` header.
- **101 Switching Protocols** — The server is switching to a different protocol
  as requested by the client (e.g., upgrading to WebSocket).
- **102 Processing** — The server is processing the request but has not yet completed
  it (WebDAV).

## 2xx — Success

These indicate that the request was successfully received, understood, and accepted.

- **200 OK** — Standard success response. The body contains the requested resource.
- **201 Created** — A new resource was successfully created. Typically returned after
  POST requests. The `Location` header usually contains the URL of the new resource.
- **204 No Content** — The request succeeded but there is no content to return.
  Common for DELETE operations or updates that don't need a response body.
- **206 Partial Content** — The server is returning only part of the resource due
  to a Range header sent by the client. Used for resumable downloads.

## 3xx — Redirection

These indicate that further action is needed to complete the request.

- **301 Moved Permanently** — The resource has been permanently moved to a new URL.
  The client should use the new URL for all future requests. Search engines transfer
  link equity to the new URL.
- **302 Found** — Temporary redirect. The resource is temporarily at a different URL.
  The client should continue using the original URL for future requests.
- **304 Not Modified** — The resource has not been modified since the last request.
  The client can use its cached version. Returned when `If-Modified-Since` or
  `If-None-Match` headers are sent.
- **307 Temporary Redirect** — Like 302 but guarantees that the HTTP method and body
  will not be changed during redirection.
- **308 Permanent Redirect** — Like 301 but guarantees the method and body won't change.

## 4xx — Client Error

These indicate that the request contains an error on the client side.

- **400 Bad Request** — The server cannot process the request due to a client error,
  such as malformed syntax, invalid request framing, or deceptive request routing.
- **401 Unauthorized** — Authentication is required but was not provided or failed.
  The response includes a `WWW-Authenticate` header indicating the auth scheme.
- **403 Forbidden** — The server understood the request but refuses to authorize it.
  Unlike 401, re-authenticating will not help. The client does not have permission.
- **404 Not Found** — The server cannot find the requested resource. This is the most
  commonly encountered error code on the web.
- **405 Method Not Allowed** — The HTTP method is not supported for the requested
  resource. For example, sending DELETE to a read-only endpoint.
- **409 Conflict** — The request conflicts with the current state of the server.
  Often used when trying to create a resource that already exists.
- **422 Unprocessable Entity** — The request is well-formed but semantically invalid.
  Common in API validation errors (e.g., missing required fields).
- **429 Too Many Requests** — The client has sent too many requests in a given time
  period (rate limiting). The `Retry-After` header may indicate when to retry.

## 5xx — Server Error

These indicate that the server failed to fulfill a valid request.

- **500 Internal Server Error** — A generic error when the server encounters an
  unexpected condition. This usually indicates a bug in the server code.
- **502 Bad Gateway** — The server, acting as a gateway or proxy, received an invalid
  response from an upstream server. Common with load balancers and reverse proxies.
- **503 Service Unavailable** — The server is temporarily unable to handle the request,
  usually due to maintenance or overload. The `Retry-After` header may be present.
- **504 Gateway Timeout** — The server, acting as a gateway, did not receive a timely
  response from the upstream server. Similar to 502 but specifically about timeouts.

## Common Patterns

### REST API Status Codes

Typical usage in REST APIs:

| Operation | Success | Common Errors |
|-----------|---------|---------------|
| GET       | 200     | 404, 401      |
| POST      | 201     | 400, 409, 422 |
| PUT       | 200     | 400, 404, 409 |
| PATCH     | 200     | 400, 404, 422 |
| DELETE    | 204     | 404, 401      |

### When to Use 401 vs 403

- **401 Unauthorized**: The client is not authenticated. "Who are you?"
- **403 Forbidden**: The client is authenticated but not authorized. "I know who you
  are, but you can't do that."

### When to Use 400 vs 422

- **400 Bad Request**: The request is syntactically malformed (bad JSON, missing content-type).
- **422 Unprocessable Entity**: The request is syntactically valid but semantically wrong
  (missing required field, invalid email format).
