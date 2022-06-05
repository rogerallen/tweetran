/* 
 * EDIT THIS LIST TO ADD MORE EXAMPLES
 */
const frag_shaders = [
  "proto/test_09.frag",
  "proto/test_10.frag",
  "proto/test_11.frag",
  "proto/test_12.frag"
];

import * as THREE from 'https://cdn.skypack.dev/pin/three@v0.128.0-rCTln0kVGE6riMrX0Nux/mode=imports/optimized/three.js';

let send_time_to_shader = false;  // boolean to control animation
let animate = document.getElementById("animate");
animate.checked = false;
animate.addEventListener('change', (event) => {
  send_time_to_shader = event.currentTarget.checked;
})

let aField = document.getElementById('aField');
let animationFactor = 1.0;
aField.value = animationFactor;
let zoomField = document.getElementById('zoomField');
let xField = document.getElementById('xField');
let yField = document.getElementById('yField');
let xyzSet = document.getElementById('xyzSet');
let reset = document.getElementById('reset');

let dropdown = document.getElementById("dropdown");
frag_shaders.forEach((s) => {
  let n = document.createElement("option")
  n.value = s;
  n.text = s;
  dropdown.appendChild(n);
});
let frag_shader_path = frag_shaders[0];

// stay similar enough to ShaderToy to be able to use code there
const uniforms = {
  iTime: { value: 0 },
  iResolution: { value: new THREE.Vector3() },
  // pan & zoom 
  uOffset: { value: new THREE.Vector2() },
  uZoom: { value: 0 }
};

// load fragment shader from file & replace default
function ShaderLoader(fragment_url, onLoad, onProgress, onError) {
  var fragment_loader = new THREE.FileLoader(THREE.DefaultLoadingManager);
  fragment_loader.setResponseType('text');
  fragment_loader.load(
    fragment_url,
    function (fragment_text) {
      onLoad(fragment_text);
    },
    onProgress,
    onError);
}

// default, boring fragment shader
const fragmentShader0 = `
void main() {
  gl_FragColor = vec4(0.5,0.5,0.5,0.0);
}
`;

// ================================================================================
// Pan zoom code starts from https://codepen.io/chengarda/pen/wRxoyB

let canvas = document.getElementById("canvas")

let cameraOffset = { x: 0.0, y: 0.0 }
xField.value = cameraOffset.x;
yField.value = cameraOffset.y;
let cameraZoom = 1
zoomField.value = cameraZoom;
let ZOOM_FACTOR = 1.1

aField.addEventListener("keyup", function (event) {
  if (event.code === "Enter") {
    event.preventDefault();
    animationFactor = aField.value;
  }
});
xyzSet.onclick = function () {
  cameraOffset.x = xField.value;
  cameraOffset.y = yField.value;
  cameraZoom = zoomField.value;
}
xField.addEventListener("keyup", function (event) {
  if (event.code === "Enter") {
    event.preventDefault();
    xyzSet.click();
  }
});
yField.addEventListener("keyup", function (event) {
  if (event.code === "Enter") {
    event.preventDefault();
    xyzSet.click();
  }
});
zoomField.addEventListener("keyup", function (event) {
  if (event.code === "Enter") {
    event.preventDefault();
    xyzSet.click();
  }
});

reset.onclick = function () {
  cameraOffset.x = 0;
  cameraOffset.y = 0;
  cameraZoom = 1;
  xField.value = cameraOffset.x;
  yField.value = cameraOffset.y;
  zoomField.value = cameraZoom;
}

// Gets the relevant location from a mouse or single touch event
function getEventLocation(e) {
  if (e.touches && e.touches.length == 1) {
    return { x: e.touches[0].clientX, y: e.touches[0].clientY }
  }
  else if (e.clientX && e.clientY) {
    return { x: e.clientX, y: e.clientY }
  }
}

let isDragging = false
let dragStart = { x: 0, y: 0 }

function onPointerDown(e) {
  isDragging = true
  //dragStart.x = getEventLocation(e).x/cameraZoom - cameraOffset.x
  //dragStart.y = getEventLocation(e).y/cameraZoom - cameraOffset.y
  dragStart.x = getEventLocation(e).x - cameraOffset.x
  dragStart.y = getEventLocation(e).y - cameraOffset.y
}

function onPointerUp(e) {
  isDragging = false
  initialPinchDistance = null
  lastZoom = cameraZoom
}

function onPointerMove(e) {
  if (isDragging) {
    //cameraOffset.x = getEventLocation(e).x/cameraZoom - dragStart.x
    //cameraOffset.y = getEventLocation(e).y/cameraZoom - dragStart.y
    cameraOffset.x = getEventLocation(e).x - dragStart.x
    cameraOffset.y = getEventLocation(e).y - dragStart.y
    xField.value = cameraOffset.x;
    yField.value = cameraOffset.y;
  }
}

function handleTouch(e, singleTouchHandler) {
  e.preventDefault();
  if (e.touches.length == 1) {
    singleTouchHandler(e)
  }
  else if (e.type == "touchmove" && e.touches.length == 2) {
    isDragging = false
    handlePinch(e)
  }
}

let initialPinchDistance = null
let lastZoom = cameraZoom

function handlePinch(e) {
  //e.preventDefault();

  let touch1 = { x: e.touches[0].clientX, y: e.touches[0].clientY }
  let touch2 = { x: e.touches[1].clientX, y: e.touches[1].clientY }

  // This is distance squared, but no need for an expensive sqrt as it's only used in ratio
  let currentDistance = (touch1.x - touch2.x) ** 2 + (touch1.y - touch2.y) ** 2

  if (initialPinchDistance == null) {
    initialPinchDistance = currentDistance
  }
  else {
    adjustZoom(null, initialPinchDistance / currentDistance)
  }
}

function adjustZoom(zoomFactor1, zoomFactor2) {
  if (!isDragging) {
    var curZoom = cameraZoom;

    if (zoomFactor1) {
      cameraZoom *= zoomFactor1
    }
    else if (zoomFactor2) {
      cameraZoom = zoomFactor2 * lastZoom
    }

    // FIXME this doesn't quite work yet
    // zoom center is at the upper left corner,
    // rather than the center of the image
    var offsetZoom = curZoom / cameraZoom;
    cameraOffset.x = cameraOffset.x * offsetZoom;
    cameraOffset.y = cameraOffset.y * offsetZoom;
    //console.log(cameraZoom, offsetZoom, cameraOffset)
    zoomField.value = cameraZoom;
  }
}

canvas.addEventListener('mousedown', onPointerDown)
canvas.addEventListener('touchstart', (e) => handleTouch(e, onPointerDown))
canvas.addEventListener('mouseup', onPointerUp)
// FIXME touchend not called on Windows+Chrome
canvas.addEventListener('touchend', (e) => handleTouch(e, onPointerUp))
canvas.addEventListener('touchcancel', (e) => handleTouch(e, onPointerUp))
canvas.addEventListener('mousemove', onPointerMove)
canvas.addEventListener('touchmove', (e) => handleTouch(e, onPointerMove))
canvas.addEventListener('wheel', (e) => {
  e.preventDefault();
  adjustZoom(e.deltaY > 0 ? 1.0 / ZOOM_FACTOR : ZOOM_FACTOR); // match ceegeemee gui
})

// ================================================================================

function main() {
  const canvas = document.querySelector('#canvas');
  const renderer = new THREE.WebGLRenderer({ canvas });
  renderer.autoClearColor = false;

  // mouse x,y origin is at top-left, make camera match
  const camera = new THREE.OrthographicCamera(
    -1, 1, // left, right
    1, -1, // top, bottom
    -1, 1  // near, far
  );
  const scene = new THREE.Scene();
  const plane = new THREE.PlaneGeometry(2, 2);
  const material = new THREE.ShaderMaterial({
    fragmentShader: fragmentShader0,
    uniforms,
  });
  const mesh = new THREE.Mesh(plane, material);
  scene.add(mesh);

  // get the real fragment shader from a file
  ShaderLoader(frag_shader_path, function (fragment_shader_text) {
    material.fragmentShader = fragment_shader_text;
    material.needsUpdate = true;
  });
  dropdown.onchange = function () {
    frag_shader_path = this.value;
    ShaderLoader(frag_shader_path, function (fragment_shader_text) {
      material.fragmentShader = fragment_shader_text;
      material.needsUpdate = true;
    });
  }

  function resizeRendererToDisplaySize(renderer) {
    const canvas = renderer.domElement;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
      renderer.setSize(width, height, false);
    }
    return needResize;
  }

  function render(time) {
    time *= 0.001;  // convert to seconds

    resizeRendererToDisplaySize(renderer);

    const canvas = renderer.domElement;
    uniforms.iResolution.value.set(canvas.width, canvas.height, 1);
    uniforms.iTime.value = send_time_to_shader ? (time / animationFactor) : 0.0;
    uniforms.uOffset.value.set(cameraOffset.x, cameraOffset.y);
    uniforms.uZoom.value = cameraZoom;

    renderer.render(scene, camera);

    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);
}

main();

