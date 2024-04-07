function removeFromPath() {
  export PATH=$(echo $PATH | sed -E -e "s;:$1;;" -e "s;$1:?;;")
}

removeFromPath "$JAVA_HOME/bin"
export JAVA_HOME=`/usr/libexec/java_home -v 11`
#export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.0.15.1.jdk/Contents/Home
export PATH=$PATH:$JAVA_HOME/bin
