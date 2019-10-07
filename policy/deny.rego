package main


deny[msg] {
  not to_number(input.spec) == 0.1
  msg = "we only support flavour spec 0.1"
}

deny[msg] {
  not input.install.artifact
  msg = "install:artifact not found"
}

deny[msg] {
  input.install.artifact == null
  msg = "install:artifact is empty"
}

deny[msg] {
  not input.install.addonname
  msg = "install:addonname not found"
}

deny[msg] {
  input.install.addonname == null
  msg = "install:addonname is empty"
}
