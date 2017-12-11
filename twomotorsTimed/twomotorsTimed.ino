#include <SoftwareSerial.h>
#include <Servo.h>
//the steps of a circle
#define STEPS 768

                  /********** INITIALIZING VARIABLES FOR STEPPER MOTORS **********/

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 170;    // variable to store the servo position

long steps = 0;
int Pin0 = 8;
int Pin1 = 9;
int Pin2 = 10;
int Pin3 = 11;
int _step = 0;
boolean dir = true;// gre


                  /********** INITIALIZING VARIABLES FOR TIME MONITORING **********/
// variable for pin connected to switch
int switchMode = 12;
int switchState = LOW;

// variable for pin connected to the button
int button = 7;
int buttonState = LOW;  // Begins not being pressed

// variables for LEDs
int redLED = 13;
int ledState = LOW;

long startCalibrationTime = 0;
long startPlayingTime = 0;

// Store the current number of page flip
int numFlips = 0;
int numFlipsPlaying = 0;

// Variouos Flags and Indicies
int firstRun = 1;
int numTimesThroughCalibration = 0;
int numTimesThroughPlaying = 0;
int prevButtonState = LOW;

// Store a list of the times to flip
//const size_t NUM_VALS = 10;
//int* flipTimes = malloc(NUM_VALS * sizeof(int));
int numPages = 5;
int flipTimes[4];

// Time when button was pressed (looking to see if held down)
unsigned long timeButtonPushed = 0;
unsigned long timeButtonReleased = 0;
int timeStart = 0;
int timeEnd = 0;
int timeForCalibration = 0;
// 1 is playing mode, 0 is calibration mode
int mode = 1;


// Variouos Flags and Indicies
int firstRunPlaying = 0;
int startMode = 0;

bool pythonResponse = false;

                  /********** HELPER FUNCTIONS FOR STEPPER MOTORS **********/
void flip(){
  for (pos = 170; pos >= 140; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 140 ; pos >= 20; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  delay(4000);
  for (pos = 20; pos <= 170; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  
}

void gomotor_forward(){
  dir = true;
  steps = 0;
  while(steps <= 170000L)
  {
    switch(_step)
     {
     case 0:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, HIGH);
     break;
     case 1:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, HIGH);
     digitalWrite(Pin3, HIGH);
     break;
     case 2:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, HIGH);
     digitalWrite(Pin3, LOW);
     break;
     case 3:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, HIGH);
     digitalWrite(Pin2, HIGH);
     digitalWrite(Pin3, LOW);
     break;
     case 4:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, HIGH);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     case 5:
     digitalWrite(Pin0, HIGH);
     digitalWrite(Pin1, HIGH);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     case 6:
     digitalWrite(Pin0, HIGH);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     case 7:
     digitalWrite(Pin0, HIGH);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, HIGH);
     break;
     default:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     }
     if(dir){
     _step++;
     }else{
     _step--;
     }
     if(_step>7){
     _step=0;
     }
     if(_step<0){
     _step=7;
     }
     delay(1);
     steps +=64;
     //Serial.println(steps);
  }
  //flip(); 
}

void gomotor_backward(){
  dir = false;
  steps = 0;
  while(steps <= 150000L)
  {
    switch(_step)
     {
     case 0:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, HIGH);
     break;
     case 1:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, HIGH);
     digitalWrite(Pin3, HIGH);
     break;
     case 2:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, HIGH);
     digitalWrite(Pin3, LOW);
     break;
     case 3:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, HIGH);
     digitalWrite(Pin2, HIGH);
     digitalWrite(Pin3, LOW);
     break;
     case 4:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, HIGH);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     case 5:
     digitalWrite(Pin0, HIGH);
     digitalWrite(Pin1, HIGH);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     case 6:
     digitalWrite(Pin0, HIGH);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     case 7:
     digitalWrite(Pin0, HIGH);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, HIGH);
     break;
     default:
     digitalWrite(Pin0, LOW);
     digitalWrite(Pin1, LOW);
     digitalWrite(Pin2, LOW);
     digitalWrite(Pin3, LOW);
     break;
     }
     if(dir){
     _step++;
     }else{
     _step--;
     }
     if(_step>7){
     _step=0;
     }
     if(_step<0){
     _step=7;
     }
     delay(1);
     steps +=64;
     //Serial.println(steps);
  }
  //flip(); 
}

void off(){
 digitalWrite(Pin0, LOW);
 digitalWrite(Pin1, LOW);
 digitalWrite(Pin2, LOW);
 digitalWrite(Pin3, LOW);
}


                              /********** SETUP **********/
void setup()
{
  /***** STEPPER SETUP ****/
  myservo.attach(2);
  // initializes stepper pins as output
  pinMode(Pin0, OUTPUT);
  pinMode(Pin1, OUTPUT);
  pinMode(Pin2, OUTPUT);
  pinMode(Pin3, OUTPUT);
  // sets stepper pins at low; OFF
  digitalWrite(Pin0, LOW);
  digitalWrite(Pin1, LOW);
  digitalWrite(Pin2, LOW);
  digitalWrite(Pin3, LOW);
  // initialize the pushbutton pin as an input
  pinMode(button, INPUT);
  // initialize serial communications at 9600 bps
  Serial.begin(9600);
  steps = 0;

  /***** BUTTON/SWITCH SETUP ****/
  // initialize the pushbutton pin as an input
  pinMode(button, INPUT);
  pinMode(switchMode, INPUT);

  pinMode(redLED, OUTPUT);

  myservo.write(pos); 
  
  // initialize serial communications at 9600 bps
  Serial.begin(9600);
}


                              /********** MAIN LOOP **********/
void loop(){
  int buttonState = digitalRead(button);
  // If this button changed states
  if(buttonState != prevButtonState){
    // Button was just pushed
    if(buttonState == HIGH){      
      timeButtonPushed = millis();  
    }
    // Button was just released
    else{
      timeButtonReleased = millis();  
    }
   }

  prevButtonState = buttonState;
  
  // If button has been pushed and released 
  if(timeButtonReleased > timeButtonPushed){
        // If we're in calibration mode
        if(!mode){
            // If button was NOT held
            if((timeButtonReleased - timeButtonPushed) < 1500){
              // **** SEND PYTHON BUTTON PRESSED **** 
              Serial.println("turn"); 
              delay(100);
              gomotor_forward();
              flip();
              gomotor_backward();
              timeButtonPushed = 0;
              timeButtonReleased = 0;
              
            }
            // Button is being held down
            else if((timeButtonReleased - timeButtonPushed) > 2000){
           
               // **** SEND PYTHON BUTTON HELD **** 
               
    
               // First time through is different, want to STAY in calibration mode, not switch to playing
               if (firstRun){
                firstRun = 0;
                timeStart = millis();
                Serial.println("stay");
                timeButtonPushed = 0;
                timeButtonReleased = 0;
               }
               else{
                // Switch modes
                 //mode = 1; 
                 Serial.println("done");
                 timeButtonPushed = 0;
                  timeButtonReleased = 0;
               }
            }
         }
         else if((timeButtonReleased - timeButtonPushed) > 900){
            Serial.println("start");
            timeButtonPushed = 0;
            timeButtonReleased = 0;
         }
         
  }
   // Playing mode (calibration is done)
   if(mode){
      if (Serial.available()){
        pythonResponse = Serial.read();

        if (pythonResponse==1){
          gomotor_forward();
          flip();
          gomotor_backward();
          delay(100);
        }
      }
   } 

  
}
