export function computeCosineSimilarity(str1: string, str2: string): number {
  // Convert strings to term frequency vectors
  const terms = new Set([...str1.split(' '), ...str2.split(' ')]);
  const v1 = Array.from(terms).map(term => str1.split(' ').filter(t => t === term).length);
  const v2 = Array.from(terms).map(term => str2.split(' ').filter(t => t === term).length);

  // Compute cosine similarity
  const dotProduct = v1.reduce((sum, a, i) => sum + a * v2[i], 0);
  const magnitude1 = Math.sqrt(v1.reduce((sum, a) => sum + a * a, 0));
  const magnitude2 = Math.sqrt(v2.reduce((sum, a) => sum + a * a, 0));

  if (magnitude1 === 0 || magnitude2 === 0) return 0;
  return dotProduct / (magnitude1 * magnitude2);
} 