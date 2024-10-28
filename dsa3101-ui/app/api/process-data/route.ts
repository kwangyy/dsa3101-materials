import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { data, ontology } = await req.json();
    console.log('Received data:', data);
    console.log('Received ontology:', ontology);

    const response = await fetch('http://127.0.0.1:5000/api/process-data', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ data, ontology }),
    });

    console.log('Response status:', response.status);
    const result = await response.json();
    console.log('Response data:', result);

    return NextResponse.json(result);
  } catch (error) {
    console.error('Detailed error:', error);
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
