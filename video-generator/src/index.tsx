import React from "react";
import {Composition, registerRoot} from "remotion";
import {A770Short} from "./short";
import {totalFrames} from "./generated";

const Root: React.FC = () => {
  return (
    <Composition
      id="A770Short"
      component={A770Short}
      durationInFrames={Math.max(1, totalFrames)}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

registerRoot(Root);
