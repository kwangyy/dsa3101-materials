import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log('Raw request body:', body);

    const { ontology: { ontology: actualOntology } } = body;
    const graphId = body.graphId;

    console.log('Extracted ontology:', actualOntology);
    console.log('Extracted graphId:', graphId);

    const response = await fetch('http://0.0.0.0:5000/api/process/ontology', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ 
        graphId, 
        ontology: actualOntology
      }),
    });

    const result = await response.json();
    console.log('API Response:', result);
    console.log('Response entityResult:', result.entityResult);
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Detailed error:', error);
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
} 