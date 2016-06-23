// Largely copied from https://github.com/dph01/scala-sbt-template


name := "Scala DSL Playing"

version := "0.1.0"

scalaVersion := "2.11.8"

organization := "jmeagher.dsl"

libraryDependencies += "org.scalactic" %% "scalactic" % "2.2.6"
libraryDependencies += "org.scalatest" %% "scalatest" % "2.2.6" % "test"
libraryDependencies += "org.scala-lang" % "scala-compiler" % scalaVersion.value % "test"

resolvers ++= Seq("snapshots"     at "http://oss.sonatype.org/content/repositories/snapshots",
                "releases"        at "http://oss.sonatype.org/content/repositories/releases"
                )
resolvers += "Artima Maven Repository" at "http://repo.artima.com/releases"
 
scalacOptions ++= Seq("-unchecked", "-deprecation")

// Extra options needed so the script manager will work, otherwise weird classloader type errors come up
fork in Test := true
javaOptions in Test += "-Dscala.usejavacp=true"
	
