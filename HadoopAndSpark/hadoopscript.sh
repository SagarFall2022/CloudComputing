cd /exports/projects/hadoop-3.3.4/
export HADOOP_CLASSPATH=${JAVA_HOME}lib/tools.jar
bin/hadoop com.sun.tools.javac.Main HadoopSort.java
jar cf hs.jar HadoopSort*.class
bin/hadoop jar hs.jar HadoopSort /home/input/ /home/output

