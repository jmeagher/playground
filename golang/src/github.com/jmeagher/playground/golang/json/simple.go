 package main

import (
	"encoding/json"
		"fmt"
		)

		type Message struct {
			Name string
				Body string
					Time int64
					}

					func main() {
						m := Message{"Alice", "Hello", 1294706395881547000}
							b, _ := json.Marshal(m)
								fmt.Println(string(b))
									json.Unmarshal(b, &m)
										var n interface{}
											json.Unmarshal([]byte(`{"Name": "Foo", "Body": "Bar", "Foo": "Something", "Time": 0}`), &n)
												fmt.Println(n)
												}

