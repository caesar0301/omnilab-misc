name := "data-prepare"

version := "1.0"

// work around with scala 1.3.0
scalaVersion := "2.10.4"

libraryDependencies += "org.apache.spark" %% "spark-core" % "1.2.0" % "provided"

libraryDependencies += "com.google.guava" % "guava" % "18.0"

libraryDependencies += "org.yaml" % "snakeyaml" % "1.15"

libraryDependencies += "joda-time" % "joda-time" % "2.7"