package jmeagher.dsl

import javax.script.ScriptEngineManager
// import scala.tools.nsc.settings.Settings

import org.scalatest._

class ScriptingTest extends FlatSpec with Matchers {

  // val settings = new Settings
  // settings.usejavacp.value = false
  
  "A simple script" should "return as expected" in {
    val e = new ScriptEngineManager().getEngineByName("scala")
    e.eval("Seq(1,2,3).length") should be (3)
  }
}
