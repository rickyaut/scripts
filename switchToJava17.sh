function removeFromPath() {
  export PATH=$(echo $PATH | sed -E -e "s;:$1;;" -e "s;$1:?;;")
}

removeFromPath "$JAVA_HOME/bin"
export JAVA_HOME=`/usr/libexec/java_home -v 17`
export PATH=$PATH:$JAVA_HOME/bin
