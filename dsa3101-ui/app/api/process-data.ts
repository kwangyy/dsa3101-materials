import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { data, ontology } = await req.json();

  try {
    // Send data to the first backend for entity extraction
    const entityResponse = await fetch('http://entity-extraction-backend-url/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data, ontology }),
    });
    const entityResult = await entityResponse.json();

    // Send data to the second backend for ontology suggestion
    const ontologyResponse = await fetch('http://ontology-suggestion-backend-url/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data }),
    });
    const ontologyResult = await ontologyResponse.json();

    return NextResponse.json({ entityResult, ontologyResult });
  } catch (error) {
    return NextResponse.json({ error: 'Error processing data' }, { status: 500 });
  }
}

