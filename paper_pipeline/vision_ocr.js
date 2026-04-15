ObjC.import('Foundation');
ObjC.import('Vision');

function normalizeBoundingBox(observation) {
  const raw = ObjC.deepUnwrap(observation.boundingBox);
  const origin = raw.origin || { x: 0, y: 0 };
  const size = raw.size || { width: 0, height: 0 };
  const x0 = origin.x;
  const x1 = origin.x + size.width;
  const y1 = 1 - origin.y;
  const y0 = y1 - size.height;
  return { x0, y0, x1, y1 };
}

function ocrImage(path) {
  const url = $.NSURL.fileURLWithPath(path);
  const request = $.VNRecognizeTextRequest.new;
  request.recognitionLevel = $.VNRequestTextRecognitionLevelAccurate;
  request.usesLanguageCorrection = true;

  const handler = $.VNImageRequestHandler.alloc.initWithURLOptions(url, $.NSDictionary.dictionary);
  const ok = handler.performRequestsError($.NSArray.arrayWithObject(request), null);
  if (!ok) {
    throw new Error(`OCR failed for ${path}`);
  }

  const observations = ObjC.unwrap(request.results);
  const lines = [];
  for (const observation of observations) {
    const candidates = ObjC.unwrap(observation.topCandidates(1));
    if (candidates.length > 0) {
      lines.push({
        text: ObjC.unwrap(candidates[0].string),
        bbox: normalizeBoundingBox(observation),
        confidence: observation.confidence
      });
    }
  }

  return {
    text: lines.map((line) => line.text).join('\n'),
    lines
  };
}

function run(argv) {
  const results = argv.map((path, index) => ({
    page: index + 1,
    image_path: path,
    ...ocrImage(path)
  }));

  return JSON.stringify(results);
}
