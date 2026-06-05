const fs = require('fs');
const path = require('path');
const createGL = require('gl');
const { PNG } = require('pngjs');

// Main function to render shader to PNG
function render(shaderText, width, height, outputPath) {
    // 1. Initialize headless WebGL context
    const gl = createGL(width, height);
    if (!gl) {
        throw new Error("WebGL context creation failed");
    }
    
    // 2. Compile Vertex Shader (draws a full screen quad)
    const vsSource = `
        attribute vec2 position;
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
    `;
    const vs = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vs, vsSource);
    gl.compileShader(vs);
    if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) {
        throw new Error("Vertex Shader compile error: " + gl.getShaderInfoLog(vs));
    }
    
    // 3. Compile Fragment Shader
    const fsShader = gl.createShader(gl.FRAGMENT_SHADER);
    const shaderTextWithPrecision = "precision mediump float;\n" + shaderText;
    gl.shaderSource(fsShader, shaderTextWithPrecision);
    gl.compileShader(fsShader);
    if (!gl.getShaderParameter(fsShader, gl.COMPILE_STATUS)) {
        throw new Error("Fragment Shader compile error: " + gl.getShaderInfoLog(fsShader));
    }
    
    // 4. Link program
    const program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fsShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        throw new Error("Program link error: " + gl.getProgramInfoLog(program));
    }
    gl.useProgram(program);
    
    // 5. Setup full-screen quad vertices
    const vertices = new Float32Array([
        -1.0, -1.0,   1.0, -1.0,  -1.0,  1.0,
        -1.0,  1.0,   1.0, -1.0,   1.0,  1.0
    ]);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    
    const posAttrib = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(posAttrib);
    gl.vertexAttribPointer(posAttrib, 2, gl.FLOAT, false, 0, 0);
    
    // 6. Bind Uniforms
    const iResolutionLoc = gl.getUniformLocation(program, 'iResolution');
    gl.uniform3f(iResolutionLoc, width, height, 1.0);
    
    const iTimeLoc = gl.getUniformLocation(program, 'iTime');
    gl.uniform1f(iTimeLoc, 0.0);
    
    const uOffsetLoc = gl.getUniformLocation(program, 'uOffset');
    gl.uniform2f(uOffsetLoc, 0.0, 0.0);
    
    const uZoomLoc = gl.getUniformLocation(program, 'uZoom');
    gl.uniform1f(uZoomLoc, 1.0);
    
    // 7. Render
    gl.viewport(0, 0, width, height);
    gl.clearColor(0.0, 0.0, 0.0, 0.0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    
    // 8. Read pixels (RGBA format)
    const pixels = new Uint8Array(width * height * 4);
    gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    
    // 9. Write to PNG (WebGL's origin is bottom-left, so invert Y to match PNG top-left)
    const png = new PNG({ width, height });
    for (let y = 0; y < height; y++) {
        const srcRow = (height - 1 - y) * width * 4;
        const destRow = y * width * 4;
        for (let x = 0; x < width * 4; x++) {
            png.data[destRow + x] = pixels[srcRow + x];
        }
    }
    
    const bufferPng = PNG.sync.write(png);
    fs.writeFileSync(outputPath, bufferPng);
}

const args = process.argv.slice(2);
if (args.length < 4) {
    console.error("Usage: node render_headless.js shader.frag width height output.png");
    process.exit(1);
}

try {
    const shaderPath = args[0];
    const width = parseInt(args[1]);
    const height = parseInt(args[2]);
    const outputPath = args[3];
    const shaderText = fs.readFileSync(shaderPath, 'utf8');
    render(shaderText, width, height, outputPath);
    console.log("SUCCESS");
} catch (err) {
    console.error("ERROR:", err.message);
    process.exit(1);
}
