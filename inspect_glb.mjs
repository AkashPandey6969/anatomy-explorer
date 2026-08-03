// Deep inspection of the high-detail source model
import { readFileSync } from 'fs';

const buf = readFileSync('./frontend/public/ct_derived_human_skeleton.glb');
const chunk0Length = buf.readUInt32LE(12);
const jsonStr = buf.slice(20, 20 + chunk0Length).toString('utf8');
const gltf = JSON.parse(jsonStr);

console.log('\n=== GLTF Asset Info ===');
console.log('Version:', gltf.asset?.version, '|', gltf.asset?.generator || '');
console.log('Total nodes:', gltf.nodes?.length);
console.log('Total meshes:', gltf.meshes?.length);
console.log('Total materials:', gltf.materials?.length);

console.log('\n=== ALL MESHES ===');
gltf.meshes?.forEach((m, i) => {
  console.log(`  [${i}] "${m.name}" — ${m.primitives?.length} primitives`);
});

console.log('\n=== ALL NODES ===');
gltf.nodes?.forEach((n, i) => {
  const hasMesh = n.mesh !== undefined;
  const meshName = hasMesh ? gltf.meshes[n.mesh]?.name : '';
  console.log(`  [${i}] "${n.name}" ${hasMesh ? `-> mesh: "${meshName}"` : ''}`);
});

console.log('\n=== MATERIALS ===');
gltf.materials?.forEach((m, i) => console.log(`  [${i}] "${m.name}"`));
