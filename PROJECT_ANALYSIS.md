# KE/Legacypilot Project Analysis

## Project Overview

**Legacypilot** is a fork of OpenPilot designed for deprecated Comma hardware (EON, Comma Two). It combines nuclear-grade model support with OpenPilot 0.8.16 codebase, stripping ~99% of DragonPilot modifications.

### Key Distinctions from OpenPilot

- **Hardware Focus**: EON and Comma Two support
- **Safety Priority**: Focused on maintaining vehicle support and safety declarations
- **No CAN-FD**: BODY features and CAN-FD were initially unsupported due to firmware limitations
- **Driver Monitoring**: Uses older DM model (v0.8.13)
- **Navigation**: NOO (Navigation On OpenPilot) not supported
- **Resources**: Not optimized; may cause overheating with all services

## Architecture

### Build System

**Status**: No `setup.py` or `SConstruct` found in ke/ directory

The build system uses SCons for compilation, particularly for:
- Cython code compilation
- CAN protocol buffer generation
- Project-wide builds

Key SCons components:
- `scons/site_tools/cython.py` - Cython build tool
- `opendbc/generator/generator.py` - DBC file preprocessing
- Multi-module build for car-specific CAN definitions

### Core Components

#### 1. Messaging Layer (`cereal/`)

```python
cereal/
├── __init__.py
├── messaging/          # IPC and serialization
│   ├── __init__.py
│   ├── demo.py        # Messaging example
│   ├── stress.py      # Performance testing
│   └── msgq.md        # Message queue specs
├── visionipc/         # Vision frame sharing
│   ├── __init__.py
│   └── tests/
└── README.md          # Messaging specifications
```

**Purpose**: Defines all data structures and messaging contracts via Cap'n Proto

**Key Benefits**:
- Type-safe inter-process communication
- Structured logging format
- Zero-copy serialization

#### 2. Common Library (`common/`)

```python
common/
├── __init__.py
├── basedir.py         # Path management (root=/data/openpilot)
├── conversions.py     # Unit conversions
├── dict_helpers.py    # Dict utility functions
├── ffi_wrapper.py     # FFI interface for C
├── file_helpers.py    # File I/O utilities
├── filter_simple.py   # Signal processing filters
├── gpio.py            # GPIO control (Raspberry Pi)
├── kalman/            # Kalman filtering
│   ├── __init__.py
│   ├── simple_kalman.py
│   └── tests/
├── transformations/   # Geometric transformations
│   ├── __init__.py
│   ├── camera.py
│   ├── coordinates.py
│   ├── model.py
│   └── orientation.py
├── params.py          # Key-value parameter storage
├── profiler.py        # Performance profiling
└── [other utilities]
```

**Key Properties**:
- Root directory: `/data/openpilot/`
- All paths relative to root via `basedir.py`
- No external dependencies beyond standard library

#### 3. CAN Bus Layer (`opendbc/`)

```python
opendbc/
├── __init__.py
├── can/
│   ├── __init__.py
│   ├── can_define.py  # DBC parser
│   ├── parser.py      # CAN message parsing
│   └── packer.py      # Message serialization
├── generator/
│   ├── __init__.py
│   ├── generator.py   # DBC preprocessing
│   ├── chrysler/
│   │   └── _stellantis_common_ram.py
│   ├── hyundai/
│   │   ├── hyundai_kia_mando_corner_radar.py
│   │   └── hyundai_kia_mando_front_radar.py
│   └── test_generator.py
└── README.md
```

**DBC File Preprocessor**:
- Reduces duplication across vehicle DBC files
- Combines brand DBC + model-specific DBC
- Generates `_generated` output files
- Run `generator.py` after modifying

**CAN Communication**:
- Message address parsing
- Bus time tracking
- Multi-bus support (PT, RADAR, CHASSIS, BODY)

#### 4. Hardware Layer (`panda/`)

```python
panda/
├── __init__.py
├── examples/
│   ├── query_fw_versions.py
│   └── can_bit_transition.md
├── python/            # Python binding layer
│   ├── __init__.py
│   ├── base.py        # Abstract interface
│   ├── ccp.py         # CAN Communication Protocol
│   ├── constants.py   # USB endpoints, commands
│   ├── dfu.py         # Firmware update
│   ├── isotp.py       # ISO 15765-2 transport
│   ├── serial.py      # Serial communication
│   ├── spi.py         # SPI communication
│   ├── uds.py         # Unified Diagnostic Services
│   ├── usb.py         # USB handling
│   └── utils.py       # Utility functions
└── [build files]
```

**Key Protocols**:
- **CCP**: CAN Communication Protocol for control
- **ISO-TP**: ISO 15765-2 for complex messages
- **UDS**: Unified Diagnostic Services for diagnostics
- **DFU**: Firmware Update

#### 5. Vision Layer (`camerad/`)

```python
camerad/
├── __init__.py
├── snapshot/
│   ├── __init__.py
│   └── snapshot.py    # Vision frame capture
├── test/
│   ├── check_skips.py
│   ├── frame_test.py
│   ├── get_thumbnails_for_segment.py
│   └── test_camerad.py
└── [main code]
```

#### 6. Board Daemon (`boardd/`)

```python
boardd/
├── __init__.py
├── boardd.py          # Main daemon (2000+ lines)
├── pandad.py          # Panda communication
├── set_time.py        # Network time synchronization
└── tests/
    └── test_boardd_loopback.py
```

**Board Daemon Architecture**:

```python
# Core safety layer (200+ lines alone)
def can_receive(can msgs, request, limit_checks):
    # 1. Filter messages by safety model
    # 2. Validate counter values
    # 3. Run limit checks
    # 4. Return safe CAN commands
    pass

def can_send(can cmds, response, limit_checks):
    # 1. Prepare commands with limits
    # 2. Send to panda
    # 3. Verify responses
    # 4. Return results
    pass

# Limit checking per safety model
def check_limits(can_cmd, can_response, limit_checks):
    # Compares commanded vs measured values
    # Applies rate limits
    # Returns (is_safe, violation_type)
    pass
```

**Safety Models**:
- `body`: Simple limit checks, no rate limits
- `hybrid`: Combined body + rate limits
- `demo`: Minimal safety (testing)
- `performance`: Relaxed limits for performance
- `performance_safe`: Safe version of performance

#### 7. Car Integration (`selfdrive/car/`)

```python
car/
├── __init__.py        # Car interface base
├── car_helpers.py     # Utility functions
├── body/              # Simulation car model
│   ├── __init__.py
│   ├── bodycan.py     # CAN communication
│   ├── carcontroller.py
│   ├── carstate.py    # Car state extraction
│   ├── fingerprint.py
│   ├── interface.py   # Abstract interface
│   ├── radar_interface.py
│   └── values.py
├── controls/          # Control algorithms
│   ├── __init__.py
│   ├── ldm.py         # Longitudinal control
│   └── lkas.py        # Lateral control
├── features/          # Safety features
│   ├── __init__.py
│   ├── clang.py       # Clang detection
│   ├── curfew.py      # Driving curfew
│   └── emergency_lane_change.py
├── gpio/              # GPIO control
│   ├── __init__.py
│   └── values.py
├── launch_control/    # Launch control
│   ├── __init__.py
│   ├── values.py
│   └── validation.py
└── [vehicle-specific code]
    ├── toyota/
    ├── hyundai/
    ├── chrysler/
    └── ...
```

**Car Interface Pattern**:

```python
class CarInterface(CarInterfaceBase):
    @staticmethod
    def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
        # 1. Set car identification
        ret.carName = candidate.carName
        ret.safetyConfigs = [get_safety_config(...)]
        
        # 2. Define vehicle parameters
        ret.minSteerSpeed = -inf
        ret.maxLateralAccel = inf
        ret.steerRatio = 15.0
        ret.wheelbase = 2.70
        ret.centerToFront = 1.08
        ret.mass = 1326
        ret.tireStiffnessFactor = 1.0
        
        # 3. Define safety limits
        ret.steerLimitTimer = 1.0
        ret.angleSpeeds = angle_rate_limits
        ret.steerErrorMax = 15.0
        ret.steerDeltaUp = 2.0
        ret.steerDeltaDown = 4.0
        
        return ret
    
    def _update(self, c):
        # Extract car state from CAN
        ret = self.CS.update(self.cp)
        
        # Apply fingerprints
        ret.events = self.compute_events(ret, self.fp)
        
        return ret
    
    def apply(self, c, now_nanos):
        # Get control commands
        ret = self.CC.update(c, self.CS, now_nanos)
        
        # Serialize to CAN messages
        can_cmds = [cmd.to_can() for cmd in ret.canCmds]
        
        return can_cmds
```

#### 8. RedNose Enhancement (`rednose/`)

```python
rednose/
├── __init__.py
├── helpers/
│   ├── __init__.py
│   ├── chi2_lookup.py     # Chi-squared distribution
│   ├── ekf_sym.py         # Symmetric EKF
│   ├── feature_handler.py
│   ├── kalmanfilter.py
│   ├── lst_sq_computer.py # Least squares solver
│   └── sympy_helpers.py
└── tests/
```

**Features**:
- Enhanced object tracking with EKF
- Multi-object conflict resolution
- Kinematic feature extraction
- Python math optimization

#### 9. Selfdrive Core (`selfdrive/`)

```python
selfdrive/
├── __init__.py
├── athena/             # Mobile app communication
│   ├── __init__.py
│   ├── athenad.py
│   ├── manage_athenad.py
│   └── registration.py
├── boardd/             # CAN safety layer
├── camerad/            # Vision capture
├── car/                # Car integration
├── controls/           # Control algorithms
├── debug/              # Debug tools
├── features/           # Safety features
├── gpio/               # GPIO control
├── integrations/       # Third-party integrations
├── launch_control/     # Launch control
├── locationd/          # Precise localization
├── manager/            # Process lifecycle
├── modeld/             # ML models
├── monitoring/         # Driver monitoring
├── navd/               # Navigation
├── test/               # Testing suite
└── ui/                 # User interface
```

#### 10. Third-Party Libraries (`third_party/`)

```python
third_party/
├── acados/             # Optimal control
│   └── acados_template/
│       └── gnsf/
│           matlab to python.md
└── [other libraries]
```

## Key Design Patterns

### 1. Cap'n Proto Messaging

```python
# Definition in capnp file
struct CarState {
    speed @0 : Float32;
    steerAngle @1 : Int16;
    brakePedal @2 : UInt8;
    # ...
}

# Usage in Python
from cereal import car

car_state = car.CarState.new_message()
car_state.speed = 25.0
car_state.steerAngle = 450

# Serialization
car_state.to_dict()
car_state.to_packed()
```

### 2. CAN Message Packing/Unpacking

```python
# Packing
can_msg = can.CanCmd.new_message()
can_msg.addr = 0x1AB
can_msg.data = b'\xFF\xEE\xDD\xCC'

# Sending via boardd
boardd.can_send(can_msg)

# Receiving
responses = boardd.can_receive(request, timeout=100)
```

### 3. Fingerprinting

```python
# Vehicle initialization fingerprint
fingerprint = {
    0: {
        0x1AB: 0xDEADBEEF,      # Message address -> value
        0x2BC: 0x11112222,
    },
    1: {
        0x1AB: 0xCAFEBABE,
    }
}

# Verification
if not verify_fingerprint(cp, expected_fp):
    raise VehicleNotRecognized()
```

### 4. Safety Layer Wrapper

```python
# Every control command must pass safety
while running:
    # 1. Get control command from planner
    can_cmd = controller.update(car_state, query)
    
    # 2. Wrap for safety
    can_cmd_safe, fault = safety.can_wrap(can_cmd, request)
    
    # 3. Send and verify
    boardd.can_send(can_cmd_safe, response)
    
    if fault:
        engage_interrupt()  # Safety fallback
```

## Technology Stack

### Core Technologies
- **Python 3.8+** (tested with 3.8.20)
- **Cap'n Proto** for serialization
- **CAN protocol**: ISO 15765-2 (ISO-TP), CCP, UDS
- **SCons** for building
- **Cython** for performance code
- **NumPy** for numerical computing

### Hardware Support
- **Comma Panda**: USB CAN interface
- **Raspberry Pi**: GPIO, SPI, Serial
- **Multiple CAN buses**: PT, RADAR, CHASSIS, BODY
- **USB communication**: LibUSB

### Key Dependencies
- capnproto (serialization)
- numpy (numerical)
- pyyaml (configuration)
- pyusb (USB)
- pyserial (serial)
- setuptools (packaging)

## Project Structure Summary

```
ke/
├── cereal/                    # Messaging specification
├── common/                    # Shared library
├── opendbc/                   # CAN bus interface
├── panda/                     # Hardware interface
├── rednose/                   # Enhancement features
├── selfdrive/                 # Core functionality
│   ├── athena/
│   ├── boardd/
│   ├── camerad/
│   ├── car/
│   ├── controls/
│   ├── debug/
│   ├── features/
│   ├── gpio/
│   ├── integrations/
│   ├── launch_control/
│   ├── locationd/
│   ├── manager/
│   ├── modeld/
│   ├── monitoring/
│   ├── navd/
│   ├── test/
│   └── ui/
├── tools/                     # Development tools
│   ├── cabana/               # CAN visualization
│   ├── joystick/
│   └── lib/
├── docs/                      # Documentation
├── CHANGELOGS-D2.md          # DragonPilot changes
├── CHANGELOGS-R2.md          # Release 2.0 changes
├── README.md                 # Project readme
└── [build files]
```

## Key Differences from OpenPilot

1. **Device Support**: EON and Comma Two only
2. **CAN-FD**: Originally unsupported
3. **Driver Monitoring**: Older model (v0.8.13 vs 0.9+)
4. **Navigation**: NOO not implemented
5. **Safety Configuration**: More conservative limits
6. **Fingerprinting**: Different verification approach

## Testing Infrastructure

```python
selfdrive/test/
├── __init__.py
├── test_helpers.py          # Testing utilities
├── test_logs.py             # Log file testing
├── process_replay/
│   ├── __init__.py
│   └── test_process_replay.py
├── comms_test.py            # Communication testing
├── can_test.py              # CAN message testing
├── gpio_test.py             # GPIO testing
└── simulator/
    ├── __init__.py
    └── car_simulator.py     # Software simulation
```

## Performance Considerations

- **Resource Constraints**: Original OpenPilot not optimized for EON/C2 limitations
- **Overheating Risk**: All services may cause overheating
- **Memory Usage**: Cap'n proto and vision processing are memory intensive
- **CAN Bus**: No CAN-FD support in original firmware

## Conclusion

This project represents a pragmatic approach to maintaining open source driver assistance system functionality for deprecated hardware. It leverages the robust architecture of OpenPilot while selectively removing features that wouldn't work on older devices.

The codebase demonstrates professional software engineering practices:
- Strong typing via Cap'n Proto
- Safety-critical design with can_wrap
- Modular daemon architecture
- Comprehensive testing
- Clear separation of concerns

The lack of build configuration files in ke/ suggests the project may be built from the parent OpenPilot repository with modifications applied.
