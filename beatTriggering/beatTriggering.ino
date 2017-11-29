/* Pressing a button will turn on the LED
 * Switch for modes
 * Holding down the button 
 */

                         /********** INITIALIZING VARIABLES **********/

// variable for pin connected to the button
int button = 10;
//int buttonState = LOW;
int prevButtonState = LOW;

// variables for LEDs
int redLED = 11;
int ledState = LOW;

// Time when button was pressed (looking to see if held down)
int timeButtonPushed = 0;
int timeButtonReleased = 0;
int timeStart = 0;
int timeEnd = 0;
int timeForCalibration = 0;

bool pythonResponse = false;

// Variouos Flags and Indicies
int firstRun = 1;
int firstRunPlaying = 1;
int numTimesThroughCalibration = 0;
int startMode = 0;

// 1 is playing mode, 0 is calibration mode
int mode = 0;


                         /********** ACTUAL CODE **********/
// Setup code here, to run once:
void setup() {
  // Button is the input
  pinMode(button, INPUT);

  // LEDs are the output
  pinMode(redLED, OUTPUT);
  Serial.begin(9600);
}

// Main code here, to run repeatedly:
void loop() {
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
            if((timeButtonReleased - timeButtonPushed) < 600){
              // **** SEND PYTHON BUTTON PRESSED **** 
              Serial.println("turn"); 
              delay(400);
            }
            // Button is being held down
            else{
               // **** SEND PYTHON BUTTON HELD **** 
               
    
               // First time through is different, want to STAY in calibration mode, not switch to playing
               if (firstRun){
                firstRun = 0;
                timeStart = millis();
                Serial.println("stay");
               }
               else{
                // Switch modes
                 mode = 1; 
                 Serial.println("done");
               }
            }
         }
         timeButtonPushed = 0;
         timeButtonReleased = 0;
  }
  
   // Playing mode (calibration is done)
    if(mode){
      // Approximate time when calibration ended
      if (firstRunPlaying){
        timeEnd = millis();

        // Time it took for calibration to run
        // i.e. expected time to be playing
        timeForCalibration = timeEnd - timeStart;
        firstRunPlaying = 0;
      }

      if (Serial.available()){
        //pythonResponse = Serial.read();
        pythonResponse = false;
      }

      
      int currentTime = millis();

      // When still in expected time to listen (5% increased bound)
      if((currentTime - timeEnd) <= (timeForCalibration)*1.05){
        if(pythonResponse){
          digitalWrite(redLED, HIGH);
          delay(200);
        }
      }
 
    }  
}
