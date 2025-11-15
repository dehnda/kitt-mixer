/*
 * CocktailMixer Pump Controller
 * 
 * Controls multiple pumps via relay module based on serial commands
 * 
 * Commands:
 * - START:<pump_id>,<duration_ms> - Start pump for specified duration
 * - STOP:<pump_id> - Stop specific pump
 * - STOP:ALL - Stop all pumps
 * - STATUS - Get current status
 * 
 * Responses:
 * - OK - Command successful
 * - ERROR:<message> - Command failed
 * - STATUS:<state> - Current status
 */

// Configuration
const int NUM_PUMPS = 8;
const int PUMP_PINS[] = {2, 3, 4, 5, 6, 7, 8, 9};  // Relay pins for pumps
const int BAUD_RATE = 9600;

// Pump state tracking
unsigned long pumpStopTimes[NUM_PUMPS];  // When each pump should stop
bool pumpActive[NUM_PUMPS];              // Whether each pump is active

void setup() {
  Serial.begin(BAUD_RATE);
  
  // Initialize pump pins as outputs
  for (int i = 0; i < NUM_PUMPS; i++) {
    pinMode(PUMP_PINS[i], OUTPUT);
    digitalWrite(PUMP_PINS[i], LOW);  // Relays off (pumps off)
    pumpActive[i] = false;
    pumpStopTimes[i] = 0;
  }
  
  Serial.println("CocktailMixer Ready");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleCommand(command);
  }
  
  // Check pump timers
  updatePumps();
}

void handleCommand(String command) {
  if (command.startsWith("START:")) {
    handleStartCommand(command.substring(6));
  } else if (command.startsWith("STOP:")) {
    handleStopCommand(command.substring(5));
  } else if (command == "STATUS") {
    handleStatusCommand();
  } else {
    Serial.println("ERROR:Unknown command");
  }
}

void handleStartCommand(String params) {
  // Parse: <pump_id>,<duration_ms>
  int commaIndex = params.indexOf(',');
  if (commaIndex == -1) {
    Serial.println("ERROR:Invalid START parameters");
    return;
  }
  
  int pumpId = params.substring(0, commaIndex).toInt();
  unsigned long duration = params.substring(commaIndex + 1).toInt();
  
  // Validate pump ID (1-indexed from Python)
  if (pumpId < 1 || pumpId > NUM_PUMPS) {
    Serial.println("ERROR:Invalid pump ID");
    return;
  }
  
  // Convert to 0-indexed
  int pumpIndex = pumpId - 1;
  
  // Start the pump
  digitalWrite(PUMP_PINS[pumpIndex], HIGH);
  pumpActive[pumpIndex] = true;
  pumpStopTimes[pumpIndex] = millis() + duration;
  
  Serial.println("OK");
}

void handleStopCommand(String params) {
  params.trim();
  
  if (params == "ALL") {
    // Stop all pumps
    for (int i = 0; i < NUM_PUMPS; i++) {
      stopPump(i);
    }
    Serial.println("OK");
  } else {
    // Stop specific pump
    int pumpId = params.toInt();
    
    if (pumpId < 1 || pumpId > NUM_PUMPS) {
      Serial.println("ERROR:Invalid pump ID");
      return;
    }
    
    int pumpIndex = pumpId - 1;
    stopPump(pumpIndex);
    Serial.println("OK");
  }
}

void handleStatusCommand() {
  // Count active pumps
  int activeCount = 0;
  for (int i = 0; i < NUM_PUMPS; i++) {
    if (pumpActive[i]) {
      activeCount++;
    }
  }
  
  if (activeCount > 0) {
    Serial.print("STATUS:mixing(");
    Serial.print(activeCount);
    Serial.println(" active)");
  } else {
    Serial.println("STATUS:idle");
  }
}

void updatePumps() {
  unsigned long currentTime = millis();
  
  for (int i = 0; i < NUM_PUMPS; i++) {
    if (pumpActive[i] && currentTime >= pumpStopTimes[i]) {
      stopPump(i);
    }
  }
}

void stopPump(int pumpIndex) {
  digitalWrite(PUMP_PINS[pumpIndex], LOW);
  pumpActive[pumpIndex] = false;
  pumpStopTimes[pumpIndex] = 0;
}
