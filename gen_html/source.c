struct Person {
  int age;
  int height;
  int weight;
};

/*
 * This is a comment to test html generation
 */
int get_age(struct Person *who) {
  return who->age;
}

int null_pointer_interproc() {
  struct Person *joe = 0;
  return get_age(joe);
}
