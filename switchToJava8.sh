function removeFromPath() {
  export PATH=$(echo $PATH | sed -E -e "s;:$1;;" -e "s;$1:?;;")
}

removeFromPath "$JAVA_HOME/bin"
#export JAVA_HOME=`/usr/libexec/java_home -v 1.8`
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_333.jdk/Contents/Home
export PATH=$PATH:$JAVA_HOME/bin
