#include <SPI.h>

//FSRs0
int fsrPin1 = 0;     // the FSR and 10K pulldown are connected to a0
int fsrReading1;     // the analog reading from the FSR resistor divider
int fsrPin2 = 1;     // the FSR and 10K pulldown are connected to a1
int fsrReading2;     // the analog reading from the FSR resistor divider
int fsrPin3 = 2;     // the FSR and 10K pulldown are connected to a2
int fsrReading3;     // the analog reading from the FSR resistor divider
int fsrPin4 = 4;     // the FSR and 10K pulldown are connected to a3
int fsrReading4;     // the analog reading from the FSR resistor divider
int Neural = 0;


//ax12a
#include <SPI.h>
#include <ServoCds55.h>
#include "pins_arduino.h"
ServoCds55 myservo;


//mg995
#include <Servo.h>
#define GrabberServo 6
Servo MG995_Servo;


void setup(void) {
  Serial.begin(9600);  
  digitalWrite(SS, HIGH);  
  SPI.begin ();
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  MG995_Servo.attach(GrabberServo); 
}
//Side note to self: 200 is back near motor, 35 is furthest out, best out is 80
//Side note to self: 150 pos is centre, I can move the motor 90 left and right of that centre. Right side is 60, Left side is 240. That is all
//Side note to self: 113 is grabber closed, 55 is wide open
void loop(void) {
  int leftSensor = 0;
  int rightSensor = 0;
  int middleSensors = 0;
  int i_value = 0;
  int other_value = 0;
  
  myservo.setVelocity(15); // set the speed of the motors

  //starting position:
  myservo.write(6,60);
  myservo.write(3,110);
  myservo.write(4,155);
  MG995_Servo.write(55);
  delay(10000);

  for (int i = 60; i<240;i++){
    fsrReading1 = analogRead(fsrPin1); //read FSR values
    if (fsrReading1 >=15 and leftSensor == 0){ // if something touches the fsr
        leftSensor = 1;
        delay(2000);
    }
    if (leftSensor == 0){
      myservo.write(6,i); //moves the arm from right side to left side
      myservo.write(4,155);
      delay(50);
      i_value = i; //gathers the final i value to know motor positon when FSR detects object
      }
    }


    
   if (leftSensor == 0){
    for (int i = 239; i>59;i--){ //this section is the opposite of the section above
      fsrReading4 = analogRead(fsrPin4); 
      if (fsrReading4 >=15 and rightSensor == 0){
          rightSensor = 1;
          delay(2000);
      }
      if (rightSensor == 0){
          myservo.write(6,i); //moves the arm from left side to right side
          myservo.write(4,155);
          delay(50);
          i_value = i;
      }  
    }
   }
   if (leftSensor == 1) { //if object is detected from right to left movement
    delay(1000);
    myservo.write(4,155);
    i_value = i_value + 14;
    other_value = i_value - 24;
    myservo.write(6,other_value);
    delay(2000);
    myservo.write(4,170);
    delay(2000);
    myservo.write(6,i_value);
    delay(2000);
    myservo.write(4,155);
    delay(3000);
   }// This section moves to position the grabber around the object
   if (rightSensor == 1) { //if object is detected from left to right movement
    delay(1000);
    myservo.write(4,155);
    i_value = i_value - 14;
    other_value = i_value + 24;
    myservo.write(6,other_value);
    delay(2000);
    myservo.write(4,170);
    delay(2000);
    myservo.write(6,i_value);
    delay(2000);
    myservo.write(4,155);
    delay(3000);
   }                       //Positions the grabber around the object
   for (int i = 55; i <113; i++){          
      fsrReading2 = analogRead(fsrPin2);
      fsrReading3 = analogRead(fsrPin3);
      
      if (fsrReading2 >=500 and fsrReading3 >=500 and middleSensors == 0){ //if something touches both middle fsrs
          middleSensors = 1;
      }
   
      if (middleSensors == 0){
        MG995_Servo.write(i);
        myservo.write(4,155);
        delay(100);
      }                          //Grabber closing, while detecting if an object is caught
  }
  delay(2000);
  if (rightSensor == 1 or leftSensor == 1){ //robot has grabbed object
    //send got
    Serial.println("g");            //sends signal to Neural Software that the object is caught
    delay(2000);
    if (Neural == 0){     
      myservo.write(4,190);
      delay(2000);
      String teststr = Serial.readString();  //read until timeout
      teststr.trim();                        
      if (teststr == "go") {                  
        myservo.write(6,240); //goes right 
      }
      else {
        myservo.write(6,60);//goes left
      }
      delay(3000);
      myservo.write(4,155);
      delay(2000);
      MG995_Servo.write(55);
      delay(2000);
      myservo.write(4,190);
      delay(2000);
      myservo.write(6,100);
      delay(3000);               //These are the movements for the object to be placed by the grabber
    }
    }
    delay(30000);               
  }
