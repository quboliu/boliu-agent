// Mark both sides of each recto break, so implicit blank versos can be detected
// without body boxes, physical-page constants or role-history queries.
#let page-role(role, running: []) = []
#let page-info() = {
  let marks = query(metadata).filter(mark => type(mark.value) == dictionary and mark.value.at("kind", default: none) == "systems-performance-running" and mark.location().page() <= here().page())
  if marks.len() == 0 { (role: "body", running: [Systems Performance]) } else { (role: "body", running: marks.last().value.running) }
}
#let is-opener() = query(metadata.where(value: "systems-performance-opener")).any(mark => mark.location().page() == here().page())
#let is-blank() = {
  let before = query(metadata.where(value: "systems-performance-before-opener"))
  let after = query(metadata.where(value: "systems-performance-opener"))
  before.zip(after).any(pair => pair.at(0).location().page() < here().page() and pair.at(1).location().page() > here().page())
}
#let page-kind() = if is-blank() { "blank" } else if is-opener() { "opener" } else { "body" }

#let recto-start(running: []) = {
  metadata("systems-performance-before-opener")
  pagebreak(to: "odd")
  metadata("systems-performance-opener")
  metadata((kind: "systems-performance-running", running: running))
}

