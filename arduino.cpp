#include <AccelStepper.h>

// --- M1: HATCH 1 (X Axis on RAMPS 1.4) ---
#define X_STEP_PIN         54
#define X_DIR_PIN          55
#define X_ENABLE_PIN       38
#define X_MIN_PIN           3  // Endstop Motor 1 (J4)

// --- M2: LINEAR GUIDE (Y Axis on RAMPS 1.4) ---
#define Y_STEP_PIN         60
#define Y_DIR_PIN          61
#define Y_ENABLE_PIN       56
#define Y_MIN_PIN          14  // Endstop Motor 2 (J6)

// --- M3: HATCH 2 (Z Axis on RAMPS 1.4) ---
#define Z_STEP_PIN         46
#define Z_DIR_PIN          48
#define Z_ENABLE_PIN       62
#define Z_MIN_PIN          18  // Endstop Motor 3 (J8)

// --- INPUT BUTTON ---
#define BUTTON_PIN          2  // Button connected to X_MAX (J5)

AccelStepper hatch1(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper linearGuide(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper hatch2(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

// --- STEP CALIBRATION (Use 'long' to prevent overflow) ---
const long STEPS_OPEN_90 = -800;           // 90 degrees to open hatches 1 and 2
const long STEPS_DROPOFF = 0;              // Position underneath the input box (Drawer 1 = 0)
const long STEPS_DRAWER_1 = 0;             // The first compartment is at the origin (0)
const long STEPS_BETWEEN_DRAWERS = 8000;   // ~10 cm between each of the 11 drawers (80000 steps = 1 m)

// Linear guide homing direction (-1000 if searching for the endstop in the same direction as the hatches)
const float GUIDE_HOMING_SPEED = -1000;
const long GUIDE_HOMING_BACKOFF = 100;

void setup() {
  Serial.begin(9600);

  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Enable all 3 motor drivers (LOW = enabled)
  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW);

  // Configure motor speeds and accelerations
  hatch1.setMaxSpeed(800);
  hatch1.setAcceleration(400);

  hatch2.setMaxSpeed(800);
  hatch2.setAcceleration(400);

  linearGuide.setMaxSpeed(3000);
  linearGuide.setAcceleration(1500);

  // 1. INITIAL HOMING ACCORDING TO THE FLOWCHART
  homeHatch(hatch1, X_MIN_PIN);
  homeHatch(hatch2, Z_MIN_PIN);
  homeLinearGuide();

  Serial.println("READY");
}

// --- SAFETY SYSTEM (EMERGENCY STOP) ---
void emergencyStop(String cause) {
  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);
  Serial.println("ERROR_EMERGENCY: " + cause);
  while (true) {} // Locks the machine until it is restarted
}

void checkSafety() {
  if (digitalRead(X_MIN_PIN) == HIGH) {
    delay(5);
    if (digitalRead(X_MIN_PIN) == HIGH) emergencyStop("Endstop 1 triggered");
  }
  if (digitalRead(Y_MIN_PIN) == HIGH) {
    delay(5);
    if (digitalRead(Y_MIN_PIN) == HIGH) emergencyStop("Endstop 2 triggered");
  }
  if (digitalRead(Z_MIN_PIN) == HIGH) {
    delay(5);
    if (digitalRead(Z_MIN_PIN) == HIGH) emergencyStop("Endstop 3 triggered");
  }
}

void moveSafely(AccelStepper &motor, long destination) {
  motor.moveTo(destination);
  while (motor.distanceToGo() != 0) {
    checkSafety();
    motor.run();
  }
}

void safeWait(unsigned long milliseconds) {
  unsigned long startTime = millis();
  while (millis() - startTime < milliseconds) {
    checkSafety();
  }
}

// --- HOMING FUNCTIONS ---
void homeHatch(AccelStepper &motor, int endstopPin) {
  motor.setSpeed(200); // Positive direction closes the hatch towards the endstop
  int confirmations = 0;
  while (confirmations < 10) {
    motor.runSpeed();
    if (digitalRead(endstopPin) == HIGH) confirmations++;
    else confirmations = 0;
  }
  motor.setCurrentPosition(0);
  delay(200);
  motor.runToNewPosition(-30); // Moves back slightly to release the switch
  motor.setCurrentPosition(0);
}

void homeLinearGuide() {
  linearGuide.setSpeed(GUIDE_HOMING_SPEED);
  int confirmations = 0;
  while (confirmations < 10) {
    linearGuide.runSpeed();
    if (digitalRead(Y_MIN_PIN) == HIGH) confirmations++;
    else confirmations = 0;
  }
  linearGuide.setCurrentPosition(0);
  delay(200);
  linearGuide.runToNewPosition(GUIDE_HOMING_BACKOFF);
  linearGuide.setCurrentPosition(0);
}

// --- MAIN LOOP ACCORDING TO THE FLOWCHART ---
void loop() {
  checkSafety();

  // Has the input button been pressed?
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(50);
    if (digitalRead(BUTTON_PIN) == LOW) {

      // 1. Clear the serial buffer and send a signal to the laptop to start OCR
      while (Serial.available() > 0) { Serial.read(); }
      Serial.println("START");

      // 2. Wait for the laptop to process the image and send the compartment number (1 to 11)
      int compartment = 0;
      while (compartment < 1 || compartment > 11) {
        checkSafety(); // Continue monitoring the endstops while the PC processes the image
        if (Serial.available() > 0) {
          String message = Serial.readStringUntil('\n');
          message.trim();
          compartment = message.toInt(); // Converts "1"..."11" into an integer
        }
      }

      // 3. Move the linear guide to the drop-off position (Drop-off = 0)
      moveSafely(linearGuide, STEPS_DROPOFF);

      // 4. Open Hatch 1
      moveSafely(hatch1, STEPS_OPEN_90);

      // 5. Wait 1 second and close Hatch 1
      safeWait(1000);
      moveSafely(hatch1, 0);

      // 6. Move the linear guide to the selected compartment (1 to 11)
      long destinationPosition = STEPS_DRAWER_1 + (STEPS_BETWEEN_DRAWERS * (long)(compartment - 1));
      moveSafely(linearGuide, destinationPosition);

      // 7. Open Hatch 2 (deliver the envelope into the drawer)
      moveSafely(hatch2, STEPS_OPEN_90);

      // 8. Wait 1 second and close Hatch 2
      safeWait(1000);
      moveSafely(hatch2, 0);

      // 9. Return the linear guide to position 0
      moveSafely(linearGuide, 0);

      // Ensure the button has been released and notify the PC that the system is back in STANDBY
      while (digitalRead(BUTTON_PIN) == LOW) { checkSafety(); }
      Serial.println("READY");
    }
  }
}
