import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log('Process Ontology - Raw request body:', body);

    const response = await fetch('http://0.0.0.0:5000/api/process/ontology', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ 
        graphId: body.graphId,
        ontology: body.ontology
      }),
    });

    const result = await response.json();
    console.log('API Response:', result);
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Detailed error:', error);
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
} 