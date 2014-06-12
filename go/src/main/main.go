package main

import (
	"os"
	"fmt"
	"io"
	"encoding/json"
)

type Settings struct {
	Name string
	Version string
	Cores int
}

// The main line
func main() {

	fmt.Println("Starting cluster bingo ...")

	fmt.Println("Collecting system settings ...")
	s := getSettings(&Settings{})

	fmt.Println("Opening output file ...")
	file, err := os.Create("results.json")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	fmt.Println("Outputing results ...")
	msg, err := outputSettings(s, file)
	if err != nil {
		panic(err)
	}

	fmt.Println("Output: \n", msg)
}

// This takes in an empty Settings struct and populates
// it according to the system's current settings
func getSettings(s *Settings)(*Settings){

	// Traverse the system and get all the relevant information
	s.Name = "Bob"
	s.Version = "1.4.1"
	s.Cores = 4

	// Return the newly populated struct
	return s
}

// This takes in the populated settings struct and 
// the desired destination, which implements Writer
func outputSettings(settings *Settings, w io.Writer)(msg string, err error){
	
	// parse the struct
	bytes, err := json.Marshal(settings)
	if err != nil{
		return "Error", err		
	}
	msg = string(bytes)

	io.WriteString(w, msg)
	return
}