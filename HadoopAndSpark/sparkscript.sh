cd /exports/projects/spark-3.3.1-bin-hadoop3
javac -cp jars/spark-core_2.12-3.3.1.jar:jars/scala-library-2.12.15.jar SparkSort.java
jar cvf SparkSort.jar SparkSort*.class

time -p bin/spark-submit --class SparkSort --master yarn --deploy-mode cluster --driver-memory 4g --executor-memory 2g --executor-cores 1 SparkSort.jar  /home/input/   /home/output/SparkSort/

