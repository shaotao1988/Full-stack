# Introduction to software architecture

> Architects pay more attention to qualities that arise from architecture choices - quality trade off

- Architect: The job title/role
- Architecting: The process of architecting/designing
- Architecture: The engineering artifact

## All programs have an architecture

Every program has an architecture, but not every architecture suits the program.

- System requirements
  - Functional needs
  - Quality needs(e.g., performance, security)
- Hard to change architecture later
  - Does not mean BDUF(Big Design Up Front)
  - But, need to think 'enough'

## Quality attributes

> A dimension of quality used to evaluate a software system, e.g., availability, throughput, scalability, modularity, security

Optimizing across many QAs is hard, must prioritize QAs

Trade-off

## Architectural styles

Examples:

- Client-Server
- Pipe-and-filter
- Map-reduce
- N-tier
- Layered
  
Benefits:

- Known tradeoffs
- Known suitability
- Compact terminology for communication

## Conceptual model

> A set of concepts that can be imposed on raw events to provide meaning and structure.

It organizes chaos

- Enables intellectual understanding
- Fits big problems into our finite minds

### Conception model of software architecture

- Model relations
  - Views & viewtypes
    - Module
        - Modules
        - Dependencies
        - Nesting
    - Runtime
        - Components
        - ConnectorsPorts
    - Allocation
        - Environmental element
        - Communication channels
  - Designation
  - Refinement
- Canonical model structure
  - Domain model: expresses intensions and concepts
  - Design model
    - Internals model: expresses the design of the system. It refines a boundary model
    - Boundary model: expresses the capabilities of the system, not design. There is only one top-level boundary model
  - Code model: expresses the solution by source code
- Quality attributes
- Design decisionsTradeoffs
- Resonsibilities
- Constraints

### Architecture vs code

When reading code, want to know:
- Who talks to who
- Messages sent and received
- Styles and patterns
- Performance requirements or guarantees
- Data structure used for communication

Easy to see in architecture model, hard to see in code

- A single object rarely has a big impact on QAs
- Cann't infer design from code
- Code-level decisions "bubble up" into QAs
- Architecture decisionskdirecty inlfluence QAs

Architctuarally evident coding style

- Current practice
  - Provide hint useful to humans
  - Use meaningful variable names
  - Intension revealing method names
- Express archtectural ideas
  - Provide hints about architecture
  - Do more than is necessary for program to compile
  - Preserve design intent
- Benefits
  - Avoid future code evolution problems
  - Imporve developer efficiency
  - Lower documetation burden
  - Improve new developer ramp-up
