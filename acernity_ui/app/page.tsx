import {CoverDemo} from "../components/cover";
import {TypewriterEffectSmoothDemo} from "../components/typewriter-effect"

// Imports directly from UI Library for further customizability
import { BackgroundGradientAnimation } from "../components/ui/background-gradient-animation";

import { WebAccess } from "./uicom";

export default function App() {

  return (
    <div>
      <CoverDemo/>

      <WebAccess/>


      <BackgroundGradientAnimation/>
      <TypewriterEffectSmoothDemo/>

    </div>
  );
}
