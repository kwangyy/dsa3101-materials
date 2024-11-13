# Knowledge Graph UI

A Next.js-based frontend interface for interacting with knowledge graphs, featuring real-time data processing and visualization.


## Prerequisites

- Node.js 16.8+ 
- Backend server running (see backend documentation)
- Modern web browser

## Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```
## Usage
1. Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

2. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.


## Features

1. **Graph Management**
   - Create new graphs with custom names
   - Delete existing graphs
   - Switch between multiple graphs

2. **Data Processing**
   - Upload text files for processing
   - Automatic entity extraction
   - Relationship mapping

3. **Interactive Interface**
   - Real-time chat with LLM
   - Graph visualization
   - Collapsible sidebar

## API Integration

The UI connects to the backend server for:
- Data processing
- Query handling
- Ontology management
- Graph storage and retrieval

## Development

The project uses:
- Next.js 14
- TypeScript
- React
- Tailwind CSS