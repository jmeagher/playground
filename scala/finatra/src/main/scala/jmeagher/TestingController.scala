package jmeagher

import com.twitter.finagle.http.Request
import com.twitter.finatra.http.Controller

class TestingController extends Controller {

  get("/ping") { request: Request =>
    "pong"
  }

  get("/name/:name") { request: Request =>
    response.ok.body("Hi " + request.params("name"))
  }

  get("/name") { request: Request =>
    response.ok.body("You didn't say your name")
  }
}
