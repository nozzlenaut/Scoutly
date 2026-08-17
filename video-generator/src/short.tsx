import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {generatedScenes, type GeneratedScene} from "./generated";

const palette = {
  bg: "#07111f",
  panel: "#101d31",
  text: "#f8fafc",
  muted: "#93a4ba",
  blue: "#5aa9ff",
  cyan: "#65e7d8",
  amber: "#ffd166",
  red: "#ff6b7d",
};

const base: React.CSSProperties = {
  fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  color: palette.text,
};

const GridBackground: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(circle at 80% 8%, rgba(90,169,255,.20), transparent 30%), radial-gradient(circle at 10% 88%, rgba(101,231,216,.14), transparent 28%), #07111f",
    }}
  >
    <AbsoluteFill
      style={{
        opacity: 0.18,
        backgroundImage:
          "linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px)",
        backgroundSize: "70px 70px",
      }}
    />
  </AbsoluteFill>
);

const Brand: React.FC = () => (
  <div
    style={{
      position: "absolute",
      top: 74,
      left: 72,
      display: "flex",
      alignItems: "center",
      gap: 16,
      fontWeight: 800,
      fontSize: 38,
      letterSpacing: -1,
    }}
  >
    <div
      style={{
        width: 42,
        height: 42,
        borderRadius: 12,
        background: `linear-gradient(135deg, ${palette.blue}, ${palette.cyan})`,
        boxShadow: "0 0 35px rgba(90,169,255,.35)",
      }}
    />
    PriceSift
  </div>
);

const Caption: React.FC<{text: string}> = ({text}) => (
  <div
    style={{
      position: "absolute",
      left: 72,
      right: 72,
      bottom: 90,
      padding: "25px 30px",
      borderRadius: 26,
      background: "rgba(5,12,24,.76)",
      border: "1px solid rgba(255,255,255,.10)",
      fontSize: 31,
      fontWeight: 650,
      lineHeight: 1.28,
      textAlign: "center",
      boxShadow: "0 22px 80px rgba(0,0,0,.25)",
    }}
  >
    {text}
  </div>
);

const DotInventory: React.FC = () => (
  <div
    style={{
      display: "grid",
      gridTemplateColumns: "repeat(6, 58px)",
      gap: 24,
      justifyContent: "center",
      marginTop: 68,
    }}
  >
    {Array.from({length: 17}).map((_, index) => (
      <div
        key={index}
        style={{
          width: 58,
          height: 58,
          borderRadius: 18,
          background: index === 0 ? palette.amber : index < 7 ? palette.cyan : palette.blue,
          boxShadow: "0 0 25px rgba(90,169,255,.20)",
        }}
      />
    ))}
  </div>
);

const PriceBars: React.FC<{kind: "spike" | "floor"}> = ({kind}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = spring({frame, fps, config: {damping: 16}});
  const leftHeight = interpolate(progress, [0, 1], [40, kind === "spike" ? 390 : 220]);
  const rightHeight = interpolate(progress, [0, 1], [40, kind === "spike" ? 540 : 220]);
  return (
    <div style={{display: "flex", alignItems: "end", justifyContent: "center", gap: 88, height: 590, marginTop: 50}}>
      <div style={{textAlign: "center"}}>
        <div style={{height: leftHeight, width: 190, borderRadius: "32px 32px 16px 16px", background: palette.cyan}} />
        <div style={{fontSize: 30, color: palette.muted, marginTop: 22}}>{kind === "spike" ? "prior" : "best"}</div>
      </div>
      <div style={{textAlign: "center"}}>
        <div style={{height: rightHeight, width: 190, borderRadius: "32px 32px 16px 16px", background: kind === "spike" ? palette.red : palette.amber}} />
        <div style={{fontSize: 30, color: palette.muted, marginTop: 22}}>{kind === "spike" ? "current" : "median"}</div>
      </div>
    </div>
  );
};

const SceneVisual: React.FC<{index: number}> = ({index}) => {
  if (index === 1) return <PriceBars kind="spike" />;
  if (index === 2) return <PriceBars kind="floor" />;
  if (index === 3) return <DotInventory />;
  if (index === 4) {
    return (
      <div style={{display: "flex", gap: 26, marginTop: 80}}>
        <div style={{flex: 1, padding: 32, borderRadius: 28, background: "rgba(255,107,125,.10)", border: "1px solid rgba(255,107,125,.30)"}}>
          <div style={{fontSize: 28, color: palette.muted}}>TYPICAL ASK</div>
          <div style={{fontSize: 68, fontWeight: 900, marginTop: 12}}>$420</div>
          <div style={{fontSize: 34, color: palette.red, fontWeight: 800}}>UP 21.4%</div>
        </div>
        <div style={{flex: 1, padding: 32, borderRadius: 28, background: "rgba(255,209,102,.10)", border: "1px solid rgba(255,209,102,.30)"}}>
          <div style={{fontSize: 28, color: palette.muted}}>LOWEST CLEAN</div>
          <div style={{fontSize: 68, fontWeight: 900, marginTop: 12}}>$299.99</div>
          <div style={{fontSize: 34, color: palette.amber, fontWeight: 800}}>STILL THERE</div>
        </div>
      </div>
    );
  }
  return (
    <div style={{marginTop: 90, display: "flex", justifyContent: "center"}}>
      <div
        style={{
          width: 700,
          height: 380,
          borderRadius: 54,
          background: "linear-gradient(145deg, #172943, #0b1525)",
          border: "2px solid rgba(255,255,255,.12)",
          boxShadow: "0 45px 110px rgba(0,0,0,.35)",
          position: "relative",
        }}
      >
        <div style={{position: "absolute", left: 54, top: 54, fontSize: 31, color: palette.muted}}>INTEL ARC</div>
        <div style={{position: "absolute", left: 54, top: 110, fontSize: 112, lineHeight: 1, fontWeight: 950, letterSpacing: -7}}>A770</div>
        <div style={{position: "absolute", left: 58, bottom: 55, fontSize: 38, color: palette.cyan, fontWeight: 800}}>16GB</div>
        <div style={{position: "absolute", right: 42, top: 72, width: 230, height: 230, borderRadius: "50%", border: "28px solid #29415f", boxShadow: "inset 0 0 0 16px #101d31"}} />
      </div>
    </div>
  );
};

const Scene: React.FC<{scene: GeneratedScene; index: number}> = ({scene, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const intro = spring({frame, fps, config: {damping: 18, stiffness: 130}});
  const opacity = interpolate(frame, [0, 5, Math.max(6, scene.frames - 5), scene.frames], [0, 1, 1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <AbsoluteFill style={{...base, opacity}}>
      <GridBackground />
      <Brand />
      <div style={{position: "absolute", top: 250, left: 72, right: 72}}>
        <div style={{fontSize: 28, color: palette.cyan, fontWeight: 850, letterSpacing: 3}}>{scene.eyebrow}</div>
        <div
          style={{
            marginTop: 24,
            whiteSpace: "pre-line",
            fontSize: index === 1 || index === 2 ? 108 : 92,
            lineHeight: 0.98,
            fontWeight: 950,
            letterSpacing: -4,
            transform: `translateY(${interpolate(intro, [0, 1], [35, 0])}px) scale(${interpolate(intro, [0, 1], [0.96, 1])})`,
          }}
        >
          {scene.headline}
        </div>
        <div style={{marginTop: 26, fontSize: 38, color: index === 1 ? palette.red : palette.muted, fontWeight: 760}}>{scene.subhead}</div>
        <SceneVisual index={index} />
      </div>
      <Caption text={scene.narration} />
      <Audio src={staticFile(scene.audio)} />
    </AbsoluteFill>
  );
};

export const A770Short: React.FC = () => {
  let cursor = 0;
  return (
    <AbsoluteFill style={base}>
      {generatedScenes.map((scene, index) => {
        const start = cursor;
        cursor += scene.frames;
        return (
          <Sequence key={scene.audio} from={start} durationInFrames={scene.frames} premountFor={30}>
            <Scene scene={scene} index={index} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
