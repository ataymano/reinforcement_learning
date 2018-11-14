#include "stdafx.h"
#include "http_server.h"

using namespace std;
using namespace web;
using namespace utility;
using namespace http;
using namespace web::http::experimental::listener;

mock_http_client::mock_http_client(const std::string& url)
  : _url(url)
  , _responders{
    { methods::GET, &mock_http_client::handle_get },
    { methods::PUT, &mock_http_client::handle_put },
    { methods::POST, &mock_http_client::handle_post },
    { methods::DEL, &mock_http_client::handle_delete },
    { methods::HEAD, &mock_http_client::handle_head },
  } {
}

const std::string& mock_http_client::get_url() const {
  return _url;
}

mock_http_client::task_t mock_http_client::request(mock_http_client::request_t request) {
  http_response resp;
  _responders[request.method()](request, resp);
  return task_t([resp]() { return resp; });
}

mock_http_client::task_t mock_http_client::request(mock_http_client::method_t method) {
  http_response resp;
  http_request request;
  _responders[method](request, resp);
  return task_t([resp]() { return resp; });
}

void mock_http_client::set_responder(http::method method, std::function<response_fn> responder) {
  _responders[method] = responder;
}

void mock_http_client::handle_get(const http_request& message, http_response& resp) {
  resp.set_status_code(status_codes::OK);
  resp.headers().add(U("Last-Modified"), datetime::utc_now().to_string());
  resp.set_body(U("Http GET response"));
}

void mock_http_client::handle_post(const http_request& message, http_response& resp) {
  resp.set_status_code(status_codes::OK);
}

void mock_http_client::handle_head(const http_request& message, http_response& resp) {
  resp.set_status_code(status_codes::OK);
  resp.headers().add(U("Last-Modified"), datetime::utc_now().to_string());
  resp.set_body(U("Http HEAD response"));
}

void mock_http_client::handle_delete(const http_request& message, http_response& resp) {
  resp.set_status_code(status_codes::OK);
}

void mock_http_client::handle_put(const http_request& message, http_response& resp) {
  resp.set_status_code(status_codes::OK);
}
