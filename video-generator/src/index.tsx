import React from "react";
import {Composition, registerRoot} from "remotion";
import {PriceSiftShort} from "./short";
import {totalFrames} from "./generated";

const Root: React.FC = () => {
  return (
    <Composition
      id="PriceSiftShort"
      component={PriceSiftShort}
      durationInFrames={Math.max(1, totalFrames)}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};

registerRoot(Root);
