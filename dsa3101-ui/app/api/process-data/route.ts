import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log('Raw request body:', body);

    const { data, graphId } = body;
    console.log('Destructured data:', data);

    if (!data) {
      console.error('No data provided');
      return NextResponse.json({ error: 'No data provided' }, { status: 400 });
    }

    const response = await fetch('http://0.0.0.0:5000/api/process/data', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ data, graphId }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      return NextResponse.json({ error: errorText }, { status: response.status });
    }

    const result = await response.json();
    console.log('Response data:', result);

    return NextResponse.json(result);
  } catch (error) {
    console.error('Detailed error:', error);
    return NextResponse.json({ error: String(error) }, { status: 500 });
  }
}
