const class_labels = {
  0: "chatting",
  1: "reading a book",
  2: "watching TV",
  3: "cocking",
  4: "hamster grinding teeth",
  5: "silence",
  6: "vacuum cleaner",
  7: "showering",
  8: "washing machine",
  9: "doing the dishes",
  10: "walking the room",
  11: "playing the piano",
  12: "going up or down the stairs",
  13: "eating snack"
}

function to_name(class_label) {
  return class_labels[class_label];
}

